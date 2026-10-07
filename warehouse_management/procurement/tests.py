from urllib import response

from django.test import TestCase

from procurement.models import PurchaseRequest, PurchaseRequestItem
from suppliers.models import Product
from procurement.serializers import PurchaseRequestSerializer
from rest_framework.test import APITestCase


class PurchaseRequestTest(TestCase):

    def setUp(self):
        self.product = Product.objects.create(
            product_code="TEST-MOU-001",
            name="Test Mouse",
            description="Test product",
            unit="PCS"
        )

    def test_purchase_request_creation(self):
        purchase_request = PurchaseRequest.objects.create(
            purchase_id="PR-TEST-001"
        )

        self.assertEqual(
            purchase_request.purchase_id,
            "PR-TEST-001"
        )

        self.assertEqual(
            purchase_request.status,
            "DRAFT"
        )

    def test_purchase_request_item_creation(self):
        product = self.product

        purchase_request = PurchaseRequest.objects.create(
            purchase_id="PR-TEST-002"
        )

        item = PurchaseRequestItem.objects.create(
            purchase_request=purchase_request,
            product=product,
            quantity=20
        )

        self.assertEqual(item.product, product)
        self.assertEqual(item.purchase_request, purchase_request)
        self.assertEqual(item.quantity, 20)




    def test_purchase_request_serializer(self):
        data = {
            "purchase_id": "PR-TEST-003",
            "items": [
                {
                    "product": self.product.id,
                    "quantity": 20
                }
            ]
        }

        serializer = PurchaseRequestSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

        purchase_request = serializer.save()

        self.assertEqual(
            purchase_request.purchase_id,
            "PR-TEST-003"
        )

        self.assertEqual(
        purchase_request.status,
        "DRAFT"
        )

        self.assertEqual(
            purchase_request.items.count(),
            1
        )

        self.assertEqual(
            purchase_request.items.first().quantity,
            20
        )

class PurchaseRequestAPITest(APITestCase):

    def setUp(self):
        self.product = Product.objects.create(
            product_code="TEST-API-001",
            name="API Test Mouse",
            description="API test product",
            unit="PCS"
        )

    def test_create_purchase_request_api(self):
        data = {
            "purchase_id": "PR-API-001",
            "items": [
                {
                    "product": self.product.id,
                    "quantity": 25
                }
            ]
        }

        response = self.client.post(
            "/api/purchase-requests/",
            data,
            format="json"
        )

        self.assertEqual(response.status_code, 201)

    def test_submit_purchase_request_api(self):
        purchase_request = PurchaseRequest.objects.create(
            purchase_id="PR-API-002"
        )

        response = self.client.post(
            f"/api/purchase-requests/{purchase_request.id}/submit/"
        )

        self.assertEqual(response.status_code, 200)

        purchase_request.refresh_from_db()

        self.assertEqual(
            purchase_request.status,
            "PENDING_APPROVAL"
        )

    def test_approve_purchase_request_creates_po(self):
        purchase_request = PurchaseRequest.objects.create(
            purchase_id="PR-API-003",
            status="PENDING_APPROVAL"
        )

        response = self.client.post(
            f"/api/purchase-requests/{purchase_request.id}/approve/"
        )

        self.assertEqual(response.status_code, 200)

        purchase_request.refresh_from_db()

        self.assertEqual(
            purchase_request.status,
            "APPROVED"
        )

        self.assertTrue(
            purchase_request.purchase_orders.exists()
        )