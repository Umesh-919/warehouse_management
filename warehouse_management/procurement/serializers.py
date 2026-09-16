from rest_framework import serializers

from .models import PurchaseRequest, PurchaseRequestItem


class PurchaseRequestItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = PurchaseRequestItem
        fields = [
            "id",
            "product",
            "quantity",
        ]


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

    def to_representation(self, instance):
        data = super().to_representation(instance)

        if instance.status != "REJECTED":
            data.pop("rejection_reason", None)

        return data
    