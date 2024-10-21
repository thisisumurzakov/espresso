from django.db.models import Q
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated

from .models import Brand, Color, Model, Vehicle
from .serializers import (
    BrandSerializer,
    ColorSerializer,
    ModelSerializer,
    VehicleSerializer,
)


class BrandListView(generics.ListCreateAPIView):
    """
    get:
    List all public brands and custom brands added by the user.

    post:
    Create a new brand with a name and logo (optional).
    """

    serializer_class = BrandSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    @swagger_auto_schema(
        operation_description="List all public and user-specific brands.",
        responses={200: BrandSerializer(many=True)},
    )
    def get_queryset(self):
        user = self.request.user
        return Brand.objects.filter(Q(user=user) | Q(user__isnull=True))

    @swagger_auto_schema(
        operation_description="Create a new brand.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["name"],
            properties={
                "name": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Brand name"
                ),
                "logo": openapi.Schema(
                    type=openapi.TYPE_FILE, description="Brand logo (optional)"
                ),
            },
        ),
        responses={
            201: BrandSerializer,
            400: "Bad request",
        },
    )
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class BrandDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    get:
    Retrieve details of a specific brand owned by the user.

    put:
    Update details of a specific brand.

    delete:
    Delete a specific brand.
    """

    serializer_class = BrandSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Retrieve a specific brand by ID.",
        responses={200: BrandSerializer},
    )
    def get_queryset(self):
        user = self.request.user
        return Brand.objects.filter(user=user)


class ModelListView(generics.ListCreateAPIView):
    """
    get:
    List all models for a given brand.

    post:
    Create a new model for a specific brand.
    """

    serializer_class = ModelSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="List all models for a given brand.",
        responses={200: ModelSerializer(many=True)},
    )
    def get_queryset(self):
        user = self.request.user
        brand_id = self.kwargs.get("pk")
        return Model.objects.filter(
            Q(user=user) | Q(user__isnull=True), brand_id=brand_id
        )

    @swagger_auto_schema(
        operation_description="Create a new model for a brand.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["name", "brand"],
            properties={
                "name": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Model name"
                ),
                "brand": openapi.Schema(
                    type=openapi.TYPE_INTEGER, description="ID of the related brand"
                ),
                "logo": openapi.Schema(
                    type=openapi.TYPE_FILE, description="Model logo (optional)"
                ),
            },
        ),
        responses={
            201: ModelSerializer,
            400: "Bad request",
        },
    )
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ModelDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    get:
    Retrieve details of a specific model owned by the user.

    put:
    Update a specific model.

    delete:
    Delete a specific model.
    """

    serializer_class = ModelSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Retrieve a specific model by ID.",
        responses={200: ModelSerializer},
    )
    def get_queryset(self):
        user = self.request.user
        return Model.objects.filter(user=user)


class ColorListView(generics.ListCreateAPIView):
    """
    get:
    List all public colors and user-specific colors.

    post:
    Create a new color.
    """

    serializer_class = ColorSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="List all public and user-specific colors.",
        responses={200: ColorSerializer(many=True)},
    )
    def get_queryset(self):
        user = self.request.user
        return Color.objects.filter(Q(user=user) | Q(user__isnull=True))

    @swagger_auto_schema(
        operation_description="Create a new color.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["name", "rgb_code"],
            properties={
                "name": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Color name"
                ),
                "rgb_code": openapi.Schema(
                    type=openapi.TYPE_STRING, description="RGB code for the color"
                ),
            },
        ),
        responses={
            201: ColorSerializer,
            400: "Bad request",
        },
    )
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ColorDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    get:
    Retrieve details of a specific color owned by the user.

    put:
    Update a specific color.

    delete:
    Delete a specific color.
    """

    serializer_class = ColorSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Retrieve a specific color by ID.",
        responses={200: ColorSerializer},
    )
    def get_queryset(self):
        user = self.request.user
        return Color.objects.filter(user=user)


class VehicleListView(generics.ListCreateAPIView):
    """
    get:
    List all vehicles owned by the user.

    post:
    Create a new vehicle with plate number, brand, model, and color.
    """

    serializer_class = VehicleSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="List all vehicles owned by the authenticated user.",
        responses={200: VehicleSerializer(many=True)},
    )
    def get_queryset(self):
        return Vehicle.objects.filter(user=self.request.user).select_related(
            "brand", "model", "color"
        )

    @swagger_auto_schema(
        operation_description="Create a new vehicle.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["plate_number", "brand", "model", "color"],
            properties={
                "plate_number": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Vehicle plate number"
                ),
                "brand": openapi.Schema(
                    type=openapi.TYPE_INTEGER, description="ID of the related brand"
                ),
                "model": openapi.Schema(
                    type=openapi.TYPE_INTEGER, description="ID of the related model"
                ),
                "color": openapi.Schema(
                    type=openapi.TYPE_INTEGER, description="ID of the related color"
                ),
            },
        ),
        responses={
            201: VehicleSerializer,
            400: "Bad request",
        },
    )
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class VehicleDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    get:
    Retrieve details of a specific vehicle owned by the user.

    put:
    Update details of a specific vehicle.

    delete:
    Delete a specific vehicle.
    """

    serializer_class = VehicleSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Retrieve a specific vehicle by ID.",
        responses={200: VehicleSerializer},
    )
    def get_queryset(self):
        return Vehicle.objects.filter(user=self.request.user).select_related(
            "brand", "model", "color"
        )
