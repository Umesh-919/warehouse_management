from django.db import models

from django.db import models


class PurchaseRequest(models.Model):
    STATUS_CHOICES = [
        ("DRAFT", "Draft"),
        ("PENDING_APPROVAL", "Pending Approval"),
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected"),
    ]

    purchase_id = models.CharField(max_length=20, unique=True)

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default="DRAFT"
    )

    rejection_reason = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.purchase_id


class PurchaseRequestItem(models.Model):
    purchase_request = models.ForeignKey(
        PurchaseRequest,
        on_delete=models.CASCADE,
        related_name="items"
    )

    product = models.ForeignKey(
        "suppliers.Product",
        on_delete=models.PROTECT
    )

    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.purchase_request.purchase_id} - {self.product.name}"
    


class PurchaseOrder(models.Model):
    STATUS_CHOICES = [
    ("DRAFT", "Draft"),
    ("SUBMITTED", "Submitted"),
    ("APPROVED", "Approved"),
    ("SENT_TO_SUPPLIER", "Sent to Supplier"),
    ("PARTIALLY_RECEIVED", "Partially Received"),
    ("RECEIVED", "Received"),
    ("CANCELLED", "Cancelled"),
]

    po_number = models.CharField(max_length=20, unique=True)

    purchase_request = models.ForeignKey(
        PurchaseRequest,
        on_delete=models.PROTECT,
        related_name="purchase_orders"
    )


    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default="DRAFT"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.po_number



class PurchaseOrderItem(models.Model):
    purchase_order = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.CASCADE,
        related_name="items"
    )

    supplier = models.ForeignKey(
    "suppliers.Supplier",
    on_delete=models.PROTECT,
    related_name="purchase_order_items",
    
)
    product = models.ForeignKey(
        "suppliers.Product",
        on_delete=models.PROTECT
    )

    ordered_quantity = models.PositiveIntegerField()

    received_quantity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.purchase_order.po_number} - {self.product.name}"