from rest_framework import serializers

from suppliers.models import Product, Supplier

from .models import PurchaseRequest, PurchaseRequestItem, PurchaseOrder, PurchaseOrderItem


class PurchaseRequestItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(
        source="product.name",
        read_only=True
    )

    class Meta:
        model = PurchaseRequestItem
        fields = ["id", "product", "product_name", "quantity"]


class PurchaseRequestSerializer(serializers.ModelSerializer):

    items = PurchaseRequestItemSerializer(many=True)

    class Meta:
        model = PurchaseRequest
        fields = [
            "id",
            "purchase_id",
            "status",
            "rejection_reason",
            "created_at",
            "items",
        ]
        read_only_fields = [
            "status",
            "rejection_reason",
            "created_at",
        ]

    def create(self, validated_data):
        items_data = validated_data.pop("items")

        purchase_request = PurchaseRequest.objects.create(
            **validated_data
        )

        for item_data in items_data:
            PurchaseRequestItem.objects.create(
                purchase_request=purchase_request,
                **item_data
            )

        return purchase_request
    

    def update(self, instance, validated_data):
        if instance.status != "DRAFT":
            raise serializers.ValidationError(
                "Only draft purchase requests can be edited."
            )
        
        items_data = validated_data.pop("items", None)

        # Update Purchase Request fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        # Update items only if items were provided
        if items_data is not None:
            instance.items.all().delete()

            for item_data in items_data:
                PurchaseRequestItem.objects.create(
                    purchase_request=instance,
                    **item_data
                )

        return instance



    
    def to_representation(self, instance):
        data = super().to_representation(instance)

        if instance.status != "REJECTED":
            data.pop("rejection_reason", None)

        return data

class RejectPurchaseRequestSerializer(serializers.Serializer):
    rejection_reason = serializers.CharField(
        required=True,
        allow_blank=False,
        trim_whitespace=True
    )


    

class PurchaseOrderItemSerializer(serializers.ModelSerializer):

    supplier_name = serializers.CharField(
        source="supplier.supplier_name",
        read_only=True
    )

    supplier_id = serializers.CharField(
        source="supplier.supplier_id",
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

    remaining_quantity = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseOrderItem
        fields = [
            "supplier_id",
            "supplier_name",
            "product_code",
            "product_name",
            "ordered_quantity",
            "received_quantity",
            "remaining_quantity",
        ]

        read_only_fields = [
            "supplier_id",
            "supplier_name",
            "product_code",
            "product_name",
            "received_quantity",
            "remaining_quantity",
        ]

    def get_remaining_quantity(self, obj):
        return obj.ordered_quantity - obj.received_quantity



class PurchaseOrderSerializer(serializers.ModelSerializer):

    items = PurchaseOrderItemSerializer(many=True)

    purchase_request = serializers.PrimaryKeyRelatedField(
        queryset=PurchaseRequest.objects.all(),
        write_only=True
    )

    class Meta:
        model = PurchaseOrder
        fields = [
            "id",
            "po_number",
            "purchase_request",
            "status",
            "created_at",
            "items",
        ]

        read_only_fields = [
            "po_number",
            "status",
            "created_at",
        ]

    def validate(self, attrs):

        purchase_request = attrs.get("purchase_request")
        items = attrs.get("items", [])

        if purchase_request.status != "APPROVED":
            raise serializers.ValidationError(
                "Purchase Order can only be created for an approved Purchase Request."
            )

        requested_quantities = {
            item.product_id: item.quantity
            for item in purchase_request.items.all()
        }

        for item in items:

            product_id = item["product"].id
            ordered_quantity = item["ordered_quantity"]

            if product_id not in requested_quantities:
                raise serializers.ValidationError(
                    f"Product {product_id} is not present in the Purchase Request."
                )

            if ordered_quantity <= 0:
                raise serializers.ValidationError(
                    "Ordered quantity must be greater than zero."
                )

            if ordered_quantity > requested_quantities[product_id]:
                raise serializers.ValidationError(
                    f"Ordered quantity for product {product_id} "
                    f"cannot exceed the requested quantity."
                )

        return attrs

    def create(self, validated_data):

        items_data = validated_data.pop("items")

        last_po = PurchaseOrder.objects.order_by("-id").first()

        if last_po:
            last_number = int(last_po.po_number.split("-")[1])
            next_number = last_number + 1
        else:
            next_number = 1

        po_number = f"PO-{next_number:03d}"

        purchase_order = PurchaseOrder.objects.create(
            po_number=po_number,
            **validated_data
        )

        for item_data in items_data:
            PurchaseOrderItem.objects.create(
                purchase_order=purchase_order,
                **item_data
            )

        return purchase_order

    def to_representation(self, instance):
        data = super().to_representation(instance)

        suppliers = {}

        for item in instance.items.select_related(
            "supplier",
            "product"
        ).all():

            supplier_id = item.supplier.supplier_id

            if supplier_id not in suppliers:
                suppliers[supplier_id] = {
                    "supplier_id": supplier_id,
                    "supplier_name": item.supplier.supplier_name,
                    "items": []
            }

            suppliers[supplier_id]["items"].append({
                "product_code": item.product.product_code,
                "product_name": item.product.name,
                "ordered_quantity": item.ordered_quantity,
                "received_quantity": item.received_quantity,
                "remaining_quantity": (
                    item.ordered_quantity - item.received_quantity
                )
            })

        data.pop("items", None)

        data["purchase_id"] = instance.purchase_request.purchase_id

        data["suppliers"] = list(suppliers.values())

        return data