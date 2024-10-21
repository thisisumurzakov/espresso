from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from products.models import Category, Option, OptionGroup, Product, ProductOption
from shops.models import Branch, Shop

User = get_user_model()


class CategoryTests(APITestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            phone_number="+1234567890", password="password"
        )
        # Create test categories
        self.category1 = Category.objects.create(name="Coffee", is_active=True)
        self.category2 = Category.objects.create(name="Tea", is_active=True)
        self.category3 = Category.objects.create(
            name="Juices", is_active=False
        )  # Inactive category

    def test_list_categories(self):
        """Test to list active categories"""
        self.client.force_authenticate(user=self.user)
        url = reverse("category-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Only 2 active categories
        self.assertEqual(response.data[0]["name"], "Coffee")
        self.assertEqual(response.data[1]["name"], "Tea")


class ProductTests(APITestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            phone_number="+1234567890", password="password"
        )
        # Create a test shop
        self.shop = Shop.objects.create(
            name="Test Coffee Shop", is_active=True, owner=self.user
        )
        # Create a branch for the shop
        self.branch = Branch.objects.create(
            shop=self.shop, address="123 Test St", latitude=40.7128, longitude=-74.0060
        )

        # Create a test category
        self.category = Category.objects.create(name="Coffee", is_active=True)

        # Create test products
        self.product1 = Product.objects.create(
            title="Cappuccino",
            description="A nice cappuccino",
            price=5.00,
            shop=self.shop,
            category=self.category,
        )
        self.product2 = Product.objects.create(
            title="Americano",
            description="A classic americano",
            price=4.00,
            shop=self.shop,
            category=self.category,
        )

        # Create an option group
        self.option_group = OptionGroup.objects.create(name="Bean Options")

        # Create options within the group
        self.option1 = Option.objects.create(name="Decaf", group=self.option_group)
        self.option2 = Option.objects.create(
            name="Columbian Beans", group=self.option_group
        )

        # Create product option for the product
        self.product_option = ProductOption.objects.create(
            product=self.product1, option_group=self.option_group
        )

    def test_list_products(self):
        """Test to list all active products"""
        self.client.force_authenticate(user=self.user)
        url = reverse("product-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [product["title"] for product in response.data]
        self.assertIn("Cappuccino", titles)
        self.assertIn("Americano", titles)

    def test_filter_by_category(self):
        """Test to filter products by category"""
        self.client.force_authenticate(user=self.user)
        url = reverse("product-list")
        response = self.client.get(url, {"category": self.category.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(response.data), 2
        )  # Both products are in the same category

    def test_filter_by_shop(self):
        """Test to filter products by shop"""
        self.client.force_authenticate(user=self.user)
        url = reverse("product-list")
        response = self.client.get(url, {"shop": self.shop.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_filter_by_radius(self):
        """Test to filter products by radius using branch location"""
        self.client.force_authenticate(user=self.user)
        url = reverse("product-list")
        response = self.client.get(
            url, {"latitude": 40.7128, "longitude": -74.0060, "radius": 10}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Both products are within 10 km radius

    def test_product_detail(self):
        """Test to retrieve detailed product information with options"""
        self.client.force_authenticate(user=self.user)
        url = reverse("product-detail", args=[self.product1.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Cappuccino")
        self.assertEqual(len(response.data["product_options"]), 1)  # 1 ProductOption
        # Check that the OptionGroup has 2 Options
        options = response.data["product_options"][0]["option_group"]["options"]
        self.assertEqual(len(options), 2)  # 2 options available
        # Optionally, check the names of the options
        option_names = [option["name"] for option in options]
        self.assertIn("Decaf", option_names)
        self.assertIn("Columbian Beans", option_names)


class ProductOptionTests(APITestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            phone_number="+1234567890", password="password"
        )
        # Create a test shop
        self.shop = Shop.objects.create(
            name="Test Coffee Shop", is_active=True, owner=self.user
        )
        # Create a test category
        self.category = Category.objects.create(name="Coffee", is_active=True)

        # Create a test product
        self.product = Product.objects.create(
            title="Latte",
            description="A classic latte",
            price=4.50,
            shop=self.shop,
            category=self.category,
        )

        # Create an option group
        self.option_group = OptionGroup.objects.create(name="Milk Options")

        # Create options within the group
        self.option1 = Option.objects.create(
            name="Almond Milk", price_adjustment=0.50, group=self.option_group
        )
        self.option2 = Option.objects.create(
            name="Oat Milk", price_adjustment=0.60, group=self.option_group
        )

        # Create product option for the latte
        self.product_option = ProductOption.objects.create(
            product=self.product, option_group=self.option_group
        )

    def test_product_options_in_detail(self):
        """Test to ensure product options are included in the product detail view"""
        self.client.force_authenticate(user=self.user)
        url = reverse("product-detail", args=[self.product.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["product_options"]), 1)
        # Access 'name' within 'option_group'
        self.assertEqual(
            response.data["product_options"][0]["option_group"]["name"], "Milk Options"
        )
