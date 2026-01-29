from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from network.models import NetworkNode, Product

User = get_user_model()


class NetworkNodeViewSetTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="admin", email="admin@mail.com", password="pass123", is_staff=True
        )

        self.factory_node = NetworkNode.objects.create(
            name="Factory Node",
            node_type="factory",
            country="FR",
            email="test1@mail.ru",
            city= "Paris",
            street= "Taxies street",
            house_number= "1"
        )
        self.retail_node = NetworkNode.objects.create(
            name="Retail Node",
            node_type="retail",
            supplier=self.factory_node,
            country="FR",
            email="test2@mail.ru",
            city="Paris",
            street="Taxies street",
            house_number="2"
        )

        self.url_list = reverse("networknode-list")
        self.url_detail = lambda pk: reverse("networknode-detail", args=[pk])

    # LIST #######################################################
    def test_node_list_auth_required(self):
        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, 401)

    def test_node_list_ok(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, 200)
        self.assertIn("results", response.data or {})

    # CREATE #####################################################
    def test_create_node_ok(self):
        self.client.force_authenticate(self.user)
        data = {
            "name": "Entrepreneur Node",
            "node_type": "entrepreneur",
            "supplier": self.retail_node.id,
            "country": "FR",
            "email": "test3@mail.ru",
            "city": "Paris",
            "street": "Taxies street",
            "house_number": "3"
        }
        response = self.client.post(self.url_list, data)
        self.assertEqual(response.status_code, 201)

    # RETRIEVE ###################################################
    def test_retrieve_node_ok(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(self.url_detail(self.factory_node.id))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], self.factory_node.id)

    # UPDATE #####################################################
    def test_update_node_ok(self):
        self.client.force_authenticate(self.user)
        response = self.client.patch(
            self.url_detail(self.retail_node.id),
            {"name": "Updated Retail"}
        )
        self.assertEqual(response.status_code, 200)
        self.retail_node.refresh_from_db()
        self.assertEqual(self.retail_node.name, "Updated Retail")

    # DELETE #####################################################
    def test_delete_node_ok(self):
        self.client.force_authenticate(self.user)
        response = self.client.delete(self.url_detail(self.retail_node.id))
        self.assertEqual(response.status_code, 204)
        self.assertFalse(NetworkNode.objects.filter(id=self.retail_node.id).exists())


class ProductViewSetTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="admin", email="admin@mail.com", password="pass123", is_staff=True
        )

        self.node = NetworkNode.objects.create(
            name="Factory Node",
            node_type="factory",
            country="FR"
        )

        self.product = Product.objects.create(
            name="Phone",
            model="X100",
            release_date="2025-01-01",
            network_node=self.node
        )

        self.url_list = reverse("product-list")
        self.url_detail = lambda pk: reverse("product-detail", args=[pk])

    # LIST #######################################################
    def test_product_list_auth_required(self):
        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, 401)

    def test_product_list_ok(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, 200)
        self.assertIn("results", response.data or {})

    # CREATE #####################################################
    def test_create_product_ok(self):
        self.client.force_authenticate(self.user)
        data = {
            "name": "Laptop",
            "model": "L200",
            "release_date": "2025-02-01",
            "network_node": self.node.id
        }
        response = self.client.post(self.url_list, data)
        self.assertEqual(response.status_code, 201)

    # RETRIEVE ###################################################
    def test_retrieve_product_ok(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(self.url_detail(self.product.id))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], self.product.id)

    # UPDATE #####################################################
    def test_update_product_ok(self):
        self.client.force_authenticate(self.user)
        response = self.client.patch(
            self.url_detail(self.product.id),
            {"model": "L300"}
        )
        self.assertEqual(response.status_code, 200)
        self.product.refresh_from_db()
        self.assertEqual(self.product.model, "L300")

    # DELETE #####################################################
    def test_delete_product_ok(self):
        self.client.force_authenticate(self.user)
        response = self.client.delete(self.url_detail(self.product.id))
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Product.objects.filter(id=self.product.id).exists())
