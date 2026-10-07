from rest_framework import serializers
from .models import Supplier, SupplierProduct, Product


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = "__all__"


class SupplierProductSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(
        source="supplier.supplier_name",
        read_only=True
    )

    product_name = serializers.CharField(
        source="product.name",
        read_only=True
    )

    product_code = serializers.CharField(
        source="product.product_code",
        read_only=True
    )

    class Meta:
        model = SupplierProduct
        fields = [
            "id",
            "supplier",
            "supplier_name",
            "product",
            "product_name",
            "product_code",
            "description",
            "purchase_price",
            "lead_time_days",
            "is_active",
        ]



class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"