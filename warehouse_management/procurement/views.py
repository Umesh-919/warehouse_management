from django.http import request
from django.shortcuts import render

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import PurchaseRequest
from .serializers import PurchaseRequestSerializer


class PurchaseRequestViewSet(viewsets.ModelViewSet):
    queryset = PurchaseRequest.objects.all()
    serializer_class = PurchaseRequestSerializer

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

        return Response(
            PurchaseRequestSerializer(purchase_request).data
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