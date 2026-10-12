
from django.test import TestCase
from suppliers.models import Supplier


class SupplierModelTest(TestCase):

    def test_supplier_creation(self):
        supplier = Supplier.objects.create(
            supplier_id="SUP-TEST",
            supplier_name="Test Supplier",
            email="test@example.com",
            phone="9876543210",
            address="Test Address",
            city="Hyderabad",
            state="Telangana",
            country="India",
            is_active=True
        )

        self.assertEqual(supplier.supplier_id, "SUP-TEST")
        self.assertEqual(supplier.supplier_name, "Test Supplier")
        self.assertTrue(supplier.is_active)
