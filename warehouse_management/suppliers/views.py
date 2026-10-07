from urllib import request
from django.http import request

from django.db.migrations import serializer
from django.shortcuts import render

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response



from .models import Supplier, SupplierProduct, Product
from .serializers import SupplierSerializer, SupplierProductSerializer, ProductSerializer


class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer

    filter_backends = [filters.SearchFilter]
    search_fields = ["supplier_name", "supplier_id", "email", "phone"]

    

class SupplierProductViewSet(viewsets.ModelViewSet):

    queryset = SupplierProduct.objects.all()
    serializer_class = SupplierProductSerializer

    def list(self, request, *args, **kwargs):
        suppliers = Supplier.objects.all()

        data = []

        for supplier in suppliers:
            supplier_products = SupplierProduct.objects.filter(
                supplier=supplier,
                is_active=True
            )

            if supplier_products.exists():
                data.append({
                    "supplier_id": supplier.supplier_id,
                    "supplier_name": supplier.supplier_name,
                    "products": [
                        {
                            "product_name": product.product.name,
                            "product_code": product.product.product_code,
                            "purchase_price": product.purchase_price,
                            "lead_time_days": product.lead_time_days,
                        }
                        for product in supplier_products
                    ]
                })

        return Response(data)



    

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer