

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







# import pytest
# from suppliers.models import Supplier


# @pytest.mark.django_db
# def test_create_supplier():
#     supplier = Supplier.objects.create(
#         supplier_id="SUP-TEST-001",
#         supplier_name="Test Supplier",
#         email="test@example.com",
#         phone="9876543210",
#         address="Test Address",
#         city="Hyderabad",
#         state="Telangana",
#         country="India",
#         is_active=True
#     )

#     assert supplier.supplier_id == "SUP-TEST-001"
#     assert supplier.supplier_name == "Test Supplier"
#     assert supplier.email == "test@example.com"
#     assert supplier.is_active is True


    #Now let's test an important rule in your model: supplier_id must be unique.