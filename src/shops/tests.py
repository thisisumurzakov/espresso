from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from shops.models import Branch, Shop

User = get_user_model()


class ShopTests(APITestCase):
    def setUp(self):
        self.owner_user = User.objects.create_user(
            phone_number="+1234567890", password="password", role="owner"
        )
        self.normal_user = User.objects.create_user(
            phone_number="+0987654321", password="password", role="user"
        )
        self.shop_url = reverse("shop-list")

    def test_create_shop_owner(self):
        self.client.force_authenticate(user=self.owner_user)
        data = {"name": "Coffee Shop", "description": "Best coffee in town"}
        response = self.client.post(self.shop_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_shop_user_permission_denied(self):
        self.client.force_authenticate(user=self.normal_user)
        data = {"name": "Another Shop"}
        response = self.client.post(self.shop_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_shops(self):
        Shop.objects.create(name="Shop 1", owner=self.owner_user, is_active=True)
        Shop.objects.create(name="Shop 2", owner=self.owner_user, is_active=True)
        self.client.force_authenticate(user=self.owner_user)
        response = self.client.get(self.shop_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

    def test_search_shops(self):
        Shop.objects.create(name="Coffee Corner", owner=self.owner_user, is_active=True)
        Shop.objects.create(name="Tea House", owner=self.owner_user, is_active=True)
        self.client.force_authenticate(user=self.owner_user)
        response = self.client.get(f"{self.shop_url}?search=Coffee")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["name"], "Coffee Corner")


class BranchTests(APITestCase):
    def setUp(self):
        self.owner_user = User.objects.create_user(
            phone_number="+1234567890", password="password", role="owner"
        )
        self.normal_user = User.objects.create_user(
            phone_number="+0987654321", password="password", role="user"
        )
        self.shop = Shop.objects.create(name="Coffee Shop", owner=self.owner_user)
        self.branch_url = reverse(
            "branch-list-create", kwargs={"shop_pk": self.shop.id}
        )
        self.all_branches_url = reverse("branch-list")

    def test_create_branch_owner(self):
        self.client.force_authenticate(user=self.owner_user)
        data = {"address": "123 Coffee St.", "latitude": 40.7128, "longitude": -74.0060}
        response = self.client.post(self.branch_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["address"], "123 Coffee St.")

    def test_create_branch_user_permission_denied(self):
        self.client.force_authenticate(user=self.normal_user)
        data = {"address": "321 Tea St.", "latitude": 40.7128, "longitude": -74.0060}
        response = self.client.post(self.branch_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_branches(self):
        Branch.objects.create(
            shop=self.shop, address="Branch 1", latitude=40.7128, longitude=-74.0060
        )
        Branch.objects.create(
            shop=self.shop, address="Branch 2", latitude=40.7129, longitude=-74.0059
        )
        self.client.force_authenticate(user=self.owner_user)
        response = self.client.get(self.all_branches_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

    def test_list_branches_with_location_filter(self):
        Branch.objects.create(
            shop=self.shop, address="Branch 1", latitude=40.7128, longitude=-74.0060
        )
        Branch.objects.create(
            shop=self.shop, address="Branch 2", latitude=40.7130, longitude=-74.0070
        )
        self.client.force_authenticate(user=self.owner_user)
        response = self.client.get(
            f"{self.all_branches_url}?latitude=40.7128&longitude=-74.0060"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)
        # Assert that branches are sorted by distance
        self.assertEqual(response.data["results"][0]["address"], "Branch 1")

    def test_list_branches_without_location_filter(self):
        Branch.objects.create(
            shop=self.shop, address="Branch 1", latitude=40.7128, longitude=-74.0060
        )
        Branch.objects.create(
            shop=self.shop, address="Branch 2", latitude=40.7130, longitude=-74.0070
        )
        self.client.force_authenticate(user=self.owner_user)
        response = self.client.get(self.all_branches_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)
