from rest_framework import serializers

from .models import Brand, Color, Model, Vehicle


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ["id", "name", "logo", "created_at", "updated_at", "user"]


class ModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Model
        fields = ["id", "name", "brand", "created_at", "updated_at", "user"]


class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = ["id", "name", "rgb_code", "created_at", "updated_at", "user"]


class VehicleSerializer(serializers.ModelSerializer):
    brand_name = serializers.CharField(source="brand.name", read_only=True)
    model_name = serializers.CharField(source="model.name", read_only=True)
    color_name = serializers.CharField(source="color.name", read_only=True)

    class Meta:
        model = Vehicle
        fields = [
            "id",
            "plate_number",
            "brand_name",
            "model_name",
            "color_name",
            "brand",
            "model",
            "color",
            "created_at",
            "updated_at",
        ]
