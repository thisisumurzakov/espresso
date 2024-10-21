from rest_framework import serializers

from .models import Branch, Shop


class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = [
            "id",
            "name",
            "description",
            "image",
            "owner",
            "is_active",
            "created_at",
            "updated_at",
        ]
        extra_kwargs = {"owner": {"read_only": True}}


class BranchSerializer(serializers.ModelSerializer):
    shop = ShopSerializer(read_only=True)

    class Meta:
        model = Branch
        fields = [
            "id",
            "shop",
            "address",
            "latitude",
            "longitude",
            "is_active",
            "created_at",
            "updated_at",
        ]
