

from django.test import TestCase
from .models import Supplier


class SupplierModelTest(TestCase):

    def test_supplier_creation(self):
        supplier = Supplier.objects.create(
            supplier_code="SUP-TEST",
            name="Test Supplier",
            email="test@example.com",
            phone="9876543210",
            address="Main Road",
            city="Hyderabad",
            state="Telangana",
            country="India",
            is_active=True
        )

        self.assertEqual(supplier.name, "Test Supplier")
