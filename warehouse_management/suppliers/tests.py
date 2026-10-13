
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from suppliers.models import Supplier


class SupplierModelTest(TestCase):

    def setUp(self):
        """Create a supplier used by multiple tests."""
        self.supplier_data = {
            "supplier_id": "SUP-001",
            "supplier_name": "ABC Traders",
            "email": "abc@example.com",
            "phone": "9876543210",
            "address": "Madhapur",
            "city": "Hyderabad",
            "state": "Telangana",
        }

    def create_supplier(self, **overrides):
        """Create a supplier with optional field overrides."""
        data = {**self.supplier_data, **overrides}
        return Supplier.objects.create(**data)

    def test_supplier_creation(self):
        supplier = self.create_supplier()

        self.assertEqual(supplier.supplier_id, "SUP-001")
        self.assertEqual(supplier.supplier_name, "ABC Traders")
        self.assertEqual(supplier.email, "abc@example.com")
        self.assertTrue(supplier.is_active)
        self.assertEqual(supplier.country, "India")

    def test_supplier_is_saved_in_database(self):
        self.create_supplier()

        self.assertEqual(Supplier.objects.count(), 1)
        self.assertTrue(
            Supplier.objects.filter(supplier_id="SUP-001").exists()
        )

    def test_supplier_string_representation(self):
        supplier = self.create_supplier()

        self.assertEqual(
            str(supplier),
            "SUP-001 - ABC Traders"
        )

    def test_created_at_is_set_automatically(self):
        supplier = self.create_supplier()

        self.assertIsNotNone(supplier.created_at)

    def test_supplier_default_values(self):
        supplier = self.create_supplier()

        self.assertEqual(supplier.country, "India")
        self.assertTrue(supplier.is_active)

    def test_inactive_supplier(self):
        supplier = self.create_supplier(is_active=False)

        self.assertFalse(supplier.is_active)

    def test_duplicate_supplier_id_is_rejected(self):
        self.create_supplier()

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                self.create_supplier(email="second@example.com")

    def test_duplicate_email_is_rejected(self):
        self.create_supplier()

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                self.create_supplier(supplier_id="SUP-002")

    def test_invalid_email_fails_model_validation(self):
        supplier = Supplier(
            **{**self.supplier_data, "email": "invalid-email"}
        )

        with self.assertRaises(ValidationError):
            supplier.full_clean()

    def test_supplier_id_maximum_length(self):
        supplier = Supplier(
            **{
                **self.supplier_data,
                "supplier_id": "S" * 21,
            }
        )

        with self.assertRaises(ValidationError):
            supplier.full_clean()

    def test_supplier_name_maximum_length(self):
        supplier = Supplier(
            **{
                **self.supplier_data,
                "supplier_name": "A" * 151,
            }
        )

        with self.assertRaises(ValidationError):
            supplier.full_clean()

    def test_required_fields_cannot_be_blank(self):
        supplier = Supplier(
            **{
                **self.supplier_data,
                "supplier_name": "",
            }
        )

        with self.assertRaises(ValidationError):
            supplier.full_clean()

    def test_supplier_update(self):
        supplier = self.create_supplier()

        supplier.supplier_name = "Updated Traders"
        supplier.save()

        supplier.refresh_from_db()

        self.assertEqual(
            supplier.supplier_name,
            "Updated Traders"
        )








from decimal import Decimal
from django.db.models.deletion import ProtectedError

from suppliers.models import SupplierProduct, Product



class SupplierProductModelTest(TestCase):

    def setUp(self):
        # Create two suppliers
        self.supplier1 = Supplier.objects.create(
            supplier_id="SUP-MAP-001",
            supplier_name="ABC Traders",
            email="abc.map@example.com",
            phone="9876543210",
            address="Madhapur",
            city="Hyderabad",
            state="Telangana",
        )

        self.supplier2 = Supplier.objects.create(
            supplier_id="SUP-MAP-002",
            supplier_name="XYZ Traders",
            email="xyz.map@example.com",
            phone="9876543211",
            address="Gachibowli",
            city="Hyderabad",
            state="Telangana",
        )

        # Create two products
        self.product1 = Product.objects.create(
            product_code="PROD-MAP-001",
            name="Laptop",
        )

        self.product2 = Product.objects.create(
            product_code="PROD-MAP-002",
            name="Mouse",
        )

    def test_supplier_product_creation(self):
        mapping = SupplierProduct.objects.create(
            supplier=self.supplier1,
            product=self.product1,
            description="Laptop supply",
            purchase_price=Decimal("45000.00"),
            lead_time_days=7,
        )

        self.assertEqual(mapping.supplier, self.supplier1)
        self.assertEqual(mapping.product, self.product1)
        self.assertEqual(mapping.description, "Laptop supply")
        self.assertEqual(
            mapping.purchase_price, Decimal("45000.00")
        )
        self.assertEqual(mapping.lead_time_days, 7)
        self.assertTrue(mapping.is_active)

    def test_supplier_can_supply_multiple_products(self):
        SupplierProduct.objects.create(
            supplier=self.supplier1,
            product=self.product1,
            purchase_price=Decimal("45000.00"),
        )
        SupplierProduct.objects.create(
            supplier=self.supplier1,
            product=self.product2,
            purchase_price=Decimal("500.00"),
        )

        self.assertEqual(
            self.supplier1.supplier_products.count(), 2
        )

    def test_product_can_have_multiple_suppliers(self):
        SupplierProduct.objects.create(
            supplier=self.supplier1,
            product=self.product1,
            purchase_price=Decimal("45000.00"),
        )
        SupplierProduct.objects.create(
            supplier=self.supplier2,
            product=self.product1,
            purchase_price=Decimal("43000.00"),
        )

        self.assertEqual(
            self.product1.supplier_products.count(), 2
        )

    def test_each_mapping_has_its_own_purchase_price(self):
        mapping1 = SupplierProduct.objects.create(
            supplier=self.supplier1,
            product=self.product1,
            purchase_price=Decimal("45000.00"),
        )
        mapping2 = SupplierProduct.objects.create(
            supplier=self.supplier2,
            product=self.product1,
            purchase_price=Decimal("43000.00"),
        )

        self.assertEqual(
            mapping1.purchase_price, Decimal("45000.00")
        )
        self.assertEqual(
            mapping2.purchase_price, Decimal("43000.00")
        )

    def test_supplier_foreign_key_and_reverse_relation(self):
        mapping = SupplierProduct.objects.create(
            supplier=self.supplier1,
            product=self.product1,
            purchase_price=Decimal("100.00"),
        )

        self.assertEqual(mapping.supplier.pk, self.supplier1.pk)
        self.assertTrue(
            self.supplier1.supplier_products.filter(
                pk=mapping.pk
            ).exists()
        )

    def test_product_foreign_key_and_reverse_relation(self):
        mapping = SupplierProduct.objects.create(
            supplier=self.supplier1,
            product=self.product1,
            purchase_price=Decimal("100.00"),
        )

        self.assertEqual(mapping.product.pk, self.product1.pk)
        self.assertTrue(
            self.product1.supplier_products.filter(
                pk=mapping.pk
            ).exists()
        )

    def test_deleting_supplier_deletes_its_mappings(self):
        mapping = SupplierProduct.objects.create(
            supplier=self.supplier1,
            product=self.product1,
            purchase_price=Decimal("100.00"),
        )
        mapping_id = mapping.pk

        self.supplier1.delete()

        self.assertFalse(
            SupplierProduct.objects.filter(pk=mapping_id).exists()
        )

    def test_deleting_referenced_product_is_prevented(self):
        SupplierProduct.objects.create(
            supplier=self.supplier1,
            product=self.product1,
            purchase_price=Decimal("100.00"),
        )
        product_id = self.product1.pk

        with self.assertRaises(ProtectedError):
            self.product1.delete()

        self.assertTrue(
            Product.objects.filter(pk=product_id).exists()
        )

    def test_mapping_default_values(self):
        mapping = SupplierProduct.objects.create(
            supplier=self.supplier1,
            product=self.product1,
            purchase_price=Decimal("100.00"),
        )

        self.assertEqual(mapping.description, "")
        self.assertEqual(mapping.lead_time_days, 0)
        self.assertTrue(mapping.is_active)

    def test_mapping_string_representation(self):
        mapping = SupplierProduct.objects.create(
            supplier=self.supplier1,
            product=self.product1,
            purchase_price=Decimal("100.00"),
        )

        self.assertEqual(
            str(mapping), "ABC Traders - Laptop"
        )









class ProductModelTest(TestCase):

    def setUp(self):
        self.product_data = {
            "product_code": "PROD-TEST-001",
            "name": "Laptop",
            "description": "Business laptop",
            "unit": "PCS",
            "current_quantity": 20,
            "reorder_level": 5,
            "is_active": True,
        }

    def create_product(self, **overrides):
        data = {**self.product_data, **overrides}
        return Product.objects.create(**data)

    def test_product_creation(self):
        product = self.create_product()

        self.assertEqual(product.product_code, "PROD-TEST-001")
        self.assertEqual(product.name, "Laptop")
        self.assertEqual(product.description, "Business laptop")
        self.assertEqual(product.unit, "PCS")
        self.assertEqual(product.current_quantity, 20)
        self.assertEqual(product.reorder_level, 5)
        self.assertTrue(product.is_active)

    def test_product_default_values(self):
        product = Product.objects.create(
            product_code="PROD-TEST-002",
            name="Keyboard",
        )

        self.assertEqual(product.description, "")
        self.assertEqual(product.unit, "PCS")
        self.assertEqual(product.current_quantity, 0)
        self.assertEqual(product.reorder_level, 0)
        self.assertTrue(product.is_active)

    def test_product_code_must_be_unique(self):
        self.create_product()

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                self.create_product(name="Another Laptop")

    def test_product_string_representation(self):
        product = self.create_product()

        self.assertEqual(str(product), "PROD-TEST-001 - Laptop")

    def test_product_update(self):
        product = self.create_product()

        product.name = "Updated Laptop"
        product.current_quantity = 30
        product.save()
        product.refresh_from_db()

        self.assertEqual(product.name, "Updated Laptop")
        self.assertEqual(product.current_quantity, 30)

    def test_zero_current_quantity_is_allowed(self):
        product = self.create_product(current_quantity=0)

        self.assertEqual(product.current_quantity, 0)

    def test_zero_reorder_level_is_allowed(self):
        product = self.create_product(reorder_level=0)

        self.assertEqual(product.reorder_level, 0)

    def test_negative_current_quantity_fails_validation(self):
        product = Product(
            **{
                **self.product_data,
                "current_quantity": -1,
            }
        )

        with self.assertRaises(ValidationError):
            product.full_clean()

    def test_negative_reorder_level_fails_validation(self):
        product = Product(
            **{
                **self.product_data,
                "reorder_level": -1,
            }
        )

        with self.assertRaises(ValidationError):
            product.full_clean()

    def test_product_name_maximum_length(self):
        product = Product(
            **{
                **self.product_data,
                "name": "A" * 151,
            }
        )

        with self.assertRaises(ValidationError):
            product.full_clean()

    def test_product_code_maximum_length(self):
        product = Product(
            **{
                **self.product_data,
                "product_code": "P" * 51,
            }
        )

        with self.assertRaises(ValidationError):
            product.full_clean()
