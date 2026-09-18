from django.db import models



class Supplier(models.Model):
    supplier_code = models.CharField(max_length=20,unique=True)

    name = models.CharField(max_length=150)

    email = models.EmailField(unique=True)

    phone = models.CharField(max_length=15)

    address = models.TextField()

    city = models.CharField(max_length=100)

    state = models.CharField(max_length=100)

    country = models.CharField(max_length=100,default="India")

    is_active = models.BooleanField(default=True)


    def __str__(self):
        return f"{self.supplier_code} - {self.name}"





class SupplierProduct(models.Model):
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        related_name="supplier_products"
    )

    product_name = models.CharField(max_length=150)
    product_code = models.CharField(max_length=50)
    description = models.TextField(blank=True)

    purchase_price = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    minimum_order_quantity = models.PositiveIntegerField(default=1)
    lead_time_days = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.supplier.name} - {self.product_name}"





class Product(models.Model):
    product_code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    unit = models.CharField(max_length=20, default="PCS")

    current_quantity = models.PositiveIntegerField(default=0)
    reorder_level = models.PositiveIntegerField(default=0)


    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.product_code} - {self.name}"