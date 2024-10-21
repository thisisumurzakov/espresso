from django.db.models import ExpressionWrapper, F, FloatField
from django.db.models.functions import ACos, Cos, Radians, Sin
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import Category, Product
from .serializers import CategorySerializer, ProductDetailSerializer, ProductSerializer


class CategoryListView(generics.ListAPIView):
    """
    GET: Returns a list of all active categories.
    """

    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Retrieve a list of all active categories.",
        responses={200: CategorySerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        """
        Swagger documentation for the GET method.
        """
        return super().get(request, *args, **kwargs)


class ProductListView(generics.ListAPIView):
    """
    GET: Returns a list of products.
    Supports filtering by category, shop, and radius (based on branch location).
    """

    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Retrieve a list of products, filtered by category, shop, and radius (branch location).",
        manual_parameters=[
            openapi.Parameter(
                "category",
                openapi.IN_QUERY,
                description="Filter by category ID",
                type=openapi.TYPE_INTEGER,
            ),
            openapi.Parameter(
                "shop",
                openapi.IN_QUERY,
                description="Filter by shop ID",
                type=openapi.TYPE_INTEGER,
            ),
            openapi.Parameter(
                "latitude",
                openapi.IN_QUERY,
                description="Latitude of user location",
                type=openapi.TYPE_NUMBER,
            ),
            openapi.Parameter(
                "longitude",
                openapi.IN_QUERY,
                description="Longitude of user location",
                type=openapi.TYPE_NUMBER,
            ),
            openapi.Parameter(
                "radius",
                openapi.IN_QUERY,
                description="Radius in kilometers to filter products by proximity",
                type=openapi.TYPE_NUMBER,
            ),
        ],
        responses={200: ProductSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        """
        Swagger documentation for the GET method.
        """
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = (
            Product.objects.filter(shop__is_active=True)
            .select_related("shop", "category")
            .order_by("id")
        )

        # Filter by chosen category
        category_id = self.request.query_params.get("category")
        if category_id:
            queryset = queryset.filter(category_id=category_id)

        # Filter by chosen shop
        shop_id = self.request.query_params.get("shop")
        if shop_id:
            queryset = queryset.filter(shop_id=shop_id)

        # Filter by chosen radius based on branch location
        latitude = self.request.query_params.get("latitude")
        longitude = self.request.query_params.get("longitude")
        radius = self.request.query_params.get("radius")  # in kilometers

        if latitude and longitude and radius:
            try:
                latitude = float(latitude)
                longitude = float(longitude)
                radius = float(radius)
            except ValueError:
                # Return unfiltered queryset if any values are invalid
                return queryset

            # Haversine formula for calculating the distance
            distance_expression = ExpressionWrapper(
                ACos(
                    Sin(Radians(F("shop__branches__latitude"))) * Sin(Radians(latitude))
                    + Cos(Radians(F("shop__branches__latitude")))
                    * Cos(Radians(latitude))
                    * Cos(Radians(F("shop__branches__longitude")) - Radians(longitude))
                )
                * 6371,  # Radius of Earth in kilometers
                output_field=FloatField(),
            )

            # Filter products based on the distance to branches within the given radius
            queryset = queryset.annotate(distance=distance_expression).filter(
                distance__lte=radius
            )

        return queryset


class ProductDetailView(generics.RetrieveAPIView):
    """
    GET: Returns detailed information about a product, including options.
    """

    serializer_class = ProductDetailSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "pk"

    @swagger_auto_schema(
        operation_description="Retrieve detailed information about a product, including its options.",
        responses={200: ProductDetailSerializer},
    )
    def get(self, request, *args, **kwargs):
        """
        Swagger documentation for the GET method.
        """
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return (
            Product.objects.filter(shop__is_active=True)
            .select_related("shop", "category")
            .prefetch_related("product_options__option_group__options")
        )
