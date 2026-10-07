
from django.http import request
from django.shortcuts import render

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import viewsets, status
from django.db import models
from rest_framework.decorators import action
from rest_framework.response import Response

from .supplier_selection import create_purchase_order

from suppliers.models import Product

from .models import PurchaseRequest, PurchaseRequestItem, PurchaseOrder, PurchaseOrderItem
from .serializers import PurchaseRequestSerializer, PurchaseOrderSerializer


class PurchaseRequestViewSet(viewsets.ModelViewSet):
    queryset = PurchaseRequest.objects.all()
    serializer_class = PurchaseRequestSerializer

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["status"]

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        purchase_request = self.get_object()

        if purchase_request.status != "PENDING_APPROVAL":
            return Response(
                {
                    "detail": "Only pending purchase requests can be approved."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        purchase_request.status = "APPROVED"
        purchase_request.rejection_reason = ""
        purchase_request.save()

        try:
            purchase_order = create_purchase_order(purchase_request)
        except ValueError as e:
            purchase_request.status = "PENDING_APPROVAL"
            purchase_request.save()

            return Response(
                {
                    "detail": str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {
                "purchase_request": PurchaseRequestSerializer(
                    purchase_request
                ).data,
                "purchase_order": {
                    "po_number": purchase_order.po_number,
                    "status": purchase_order.status,
            }
        },
        status=status.HTTP_200_OK
    )
    

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        purchase_request = self.get_object()

        if purchase_request.status != "PENDING_APPROVAL":
            return Response(
              {
                  "detail": "Only pending purchase requests can be rejected."
             },
             status=status.HTTP_400_BAD_REQUEST
            )

        reason = request.data.get("rejection_reason")

        if not reason:
            return Response(
            {
                    "detail": "Rejection reason is required."
            },
            status=status.HTTP_400_BAD_REQUEST
        )

        purchase_request.status = "REJECTED"
        purchase_request.rejection_reason = reason
        purchase_request.save()

        return Response(
        PurchaseRequestSerializer(purchase_request).data
        )


    @action(detail=False, methods=["post"])
    def generate(self, request):
        from suppliers.models import Product

        products = Product.objects.filter(is_active=True)

        low_stock_products = products.filter(
            current_quantity__lt=models.F("reorder_level")
        )

        if not low_stock_products.exists():
            return Response(
                {"detail": "No products are below their reorder level."},
                status=status.HTTP_200_OK
            )

        # Generate next PR ID
        last_pr = PurchaseRequest.objects.order_by("-id").first()

        if last_pr:
            last_number = int(last_pr.purchase_id.split("-")[1])
            next_number = last_number + 1
        else:
            next_number = 1

        purchase_id = f"PR-{next_number:03d}"

        # Create Purchase Request
        purchase_request = PurchaseRequest.objects.create(
            purchase_id=purchase_id
        )

        # Create Purchase Request Items
        for product in low_stock_products:
            suggested_quantity = (
                product.reorder_level - product.current_quantity
            )

            PurchaseRequestItem.objects.create(
            purchase_request=purchase_request,
            product=product,
            quantity=suggested_quantity
        )

        return Response(
            PurchaseRequestSerializer(purchase_request).data,
            status=status.HTTP_201_CREATED
    )

    @action(detail=True, methods=["post"])
    def submit(self, request, pk=None):
        purchase_request = self.get_object()

        if purchase_request.status != "DRAFT":
            return Response(
                {
                    "detail": "Only draft purchase requests can be submitted for approval."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        purchase_request.status = "PENDING_APPROVAL"
        purchase_request.save()

        return Response(
            PurchaseRequestSerializer(purchase_request).data
        )



class PurchaseOrderViewSet(viewsets.ModelViewSet):
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer