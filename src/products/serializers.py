from rest_framework import serializers

from .models import Category, Option, OptionGroup, Product, ProductOption


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "parent", "is_active"]


class ProductSerializer(serializers.ModelSerializer):
    shop_name = serializers.CharField(source="shop.name", read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "title",
            "description",
            "price",
            "image",
            "shop_name",
            "category_name",
        ]


class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ["id", "name", "price_adjustment"]


class OptionGroupSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True, read_only=True)

    class Meta:
        model = OptionGroup
        fields = ["id", "name", "options"]


class ProductOptionSerializer(serializers.ModelSerializer):
    option_group = OptionGroupSerializer(read_only=True)

    class Meta:
        model = ProductOption
        fields = ["option_group"]


class ProductDetailSerializer(serializers.ModelSerializer):
    shop_name = serializers.CharField(source="shop.name", read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)
    product_options = ProductOptionSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "title",
            "description",
            "price",
            "image",
            "shop_name",
            "category_name",
            "product_options",
        ]
