import io
import os
import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.urls import reverse
from PIL import Image
from rest_framework import status
from rest_framework.test import APITestCase

from vehicles.models import Brand, Color, Model, Vehicle

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp()


def generate_test_image():
    image = Image.new("RGB", (100, 100), color="red")
    byte_io = io.BytesIO()
    image.save(byte_io, "PNG")
    byte_io.seek(0)
    return SimpleUploadedFile(
        name="test_image.png", content=byte_io.read(), content_type="image/png"
    )


class BrandTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            phone_number="+1234567890", password="password"
        )
        self.url = reverse("brand-list")

    def test_create_brand(self):
        self.client.force_authenticate(user=self.user)
        data = {"name": "Toyota"}
        response = self.client.post(self.url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "Toyota")

    @override_settings(
        MEDIA_ROOT=TEMP_MEDIA_ROOT
    )  # Override the MEDIA_ROOT to a temporary directory
    def test_create_brand_with_logo(self):
        self.client.force_authenticate(user=self.user)

        # Use the image generator to create a valid image file
        logo = generate_test_image()

        data = {
            "name": "Test Brand",
            "logo": logo,
        }
        response = self.client.post(self.url, data, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_list_brands(self):
        # Create public brand
        Brand.objects.create(name="Ford")
        # Create user-specific brand
        Brand.objects.create(name="Audi", user=self.user)

        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_delete_brand(self):
        brand = Brand.objects.create(name="BMW", user=self.user)
        url = reverse("brand-detail", args=[brand.id])

        self.client.force_authenticate(user=self.user)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Ensure brand is deleted
        self.assertFalse(Brand.objects.filter(id=brand.id).exists())

    def test_delete_other_user_brand(self):
        other_user = User.objects.create_user(
            phone_number="+9876543210", password="password"
        )
        brand = Brand.objects.create(name="Tesla", user=other_user)
        url = reverse("brand-detail", args=[brand.id])

        self.client.force_authenticate(user=self.user)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def tearDown(self):
        if os.path.exists(TEMP_MEDIA_ROOT):
            shutil.rmtree(TEMP_MEDIA_ROOT)


class ModelTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            phone_number="+1234567890", password="password"
        )
        self.brand = Brand.objects.create(name="Toyota", user=self.user)
        self.url = reverse("model-list", kwargs={"pk": self.brand.id})

    def test_create_model(self):
        self.client.force_authenticate(user=self.user)
        data = {"name": "Corolla", "brand": self.brand.id}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "Corolla")

    def test_list_models(self):
        # Create public model
        Model.objects.create(name="Camry", brand=self.brand)
        # Create user-specific model
        Model.objects.create(name="Corolla", brand=self.brand, user=self.user)

        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_delete_model(self):
        model = Model.objects.create(name="Prius", brand=self.brand, user=self.user)
        url = reverse("model-detail", args=[model.id])

        self.client.force_authenticate(user=self.user)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Ensure model is deleted
        self.assertFalse(Model.objects.filter(id=model.id).exists())

    def test_delete_other_user_model(self):
        other_user = User.objects.create_user(
            phone_number="+9876543210", password="password"
        )
        model = Model.objects.create(name="Supra", brand=self.brand, user=other_user)
        url = reverse("model-detail", args=[model.id])

        self.client.force_authenticate(user=self.user)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class ColorTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            phone_number="+1234567890", password="password"
        )
        self.url = reverse("color-list")

    def test_create_color(self):
        self.client.force_authenticate(user=self.user)
        data = {"name": "Red", "rgb_code": "#FF0000"}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "Red")

    def test_list_colors(self):
        # Create public color
        Color.objects.create(name="Blue", rgb_code="#0000FF")
        # Create user-specific color
        Color.objects.create(name="Green", rgb_code="#00FF00", user=self.user)

        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_delete_color(self):
        color = Color.objects.create(name="Yellow", rgb_code="#FFFF00", user=self.user)
        url = reverse("color-detail", args=[color.id])

        self.client.force_authenticate(user=self.user)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Ensure color is deleted
        self.assertFalse(Color.objects.filter(id=color.id).exists())

    def test_delete_other_user_color(self):
        other_user = User.objects.create_user(
            phone_number="+9876543210", password="password"
        )
        color = Color.objects.create(name="Purple", rgb_code="#800080", user=other_user)
        url = reverse("color-detail", args=[color.id])

        self.client.force_authenticate(user=self.user)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class VehicleTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            phone_number="+1234567890", password="password"
        )
        self.brand = Brand.objects.create(name="Toyota")
        self.model = Model.objects.create(name="Corolla", brand=self.brand)
        self.color = Color.objects.create(name="Black", rgb_code="#000000")
        self.url = reverse("vehicle-list")

    def test_create_vehicle(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "plate_number": "XYZ123",
            "brand": self.brand.id,
            "model": self.model.id,
            "color": self.color.id,
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["plate_number"], "XYZ123")

    def test_list_vehicles(self):
        # Create user-specific vehicle
        Vehicle.objects.create(
            plate_number="ABC123",
            brand=self.brand,
            model=self.model,
            color=self.color,
            user=self.user,
        )

        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_delete_vehicle(self):
        vehicle = Vehicle.objects.create(
            plate_number="XYZ456",
            brand=self.brand,
            model=self.model,
            color=self.color,
            user=self.user,
        )
        url = reverse("vehicle-detail", args=[vehicle.id])

        self.client.force_authenticate(user=self.user)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Ensure vehicle is deleted
        self.assertFalse(Vehicle.objects.filter(id=vehicle.id).exists())

    def test_delete_other_user_vehicle(self):
        other_user = User.objects.create_user(
            phone_number="+9876543210", password="password"
        )
        vehicle = Vehicle.objects.create(
            plate_number="LMN789",
            brand=self.brand,
            model=self.model,
            color=self.color,
            user=other_user,
        )
        url = reverse("vehicle-detail", args=[vehicle.id])

        self.client.force_authenticate(user=self.user)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
