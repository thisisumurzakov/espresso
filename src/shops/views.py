from django.db.models import ExpressionWrapper, F, FloatField
from django.db.models.functions import ACos, Cos, Radians, Sin
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics
from rest_framework.exceptions import PermissionDenied
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated

from config.paginations import CustomPageNumberPagination

from .models import Branch, Shop
from .permissions import IsOwnerOrReadOnly
from .serializers import BranchSerializer, ShopSerializer


class ShopListCreateView(generics.ListCreateAPIView):
    """
    get:
    List all active shops.

    post:
    Create a new shop. Only users with the 'owner' role can create a shop.
    """

    serializer_class = ShopSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [SearchFilter]
    search_fields = ["name"]
    pagination_class = CustomPageNumberPagination

    @swagger_auto_schema(
        operation_description="List all active shops, filtered by name if query parameter 'name' is provided.",
        responses={200: ShopSerializer(many=True)},
    )
    def get_queryset(self):
        return Shop.objects.filter(is_active=True)

    @swagger_auto_schema(
        operation_description="Create a new shop. Only users with the 'owner' role can create shops.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["name"],
            properties={
                "name": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Shop name"
                ),
                "description": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Shop description (optional)"
                ),
                "image": openapi.Schema(
                    type=openapi.TYPE_FILE, description="Shop image (optional)"
                ),
            },
        ),
        responses={
            201: ShopSerializer,
            400: "Bad request",
        },
    )
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class BranchListByShopIdCreateView(generics.ListCreateAPIView):
    """
    get:
    List all branches for a specific shop.

    post:
    Create a new branch for a shop. Only the owner of the shop can create branches.
    """

    serializer_class = BranchSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    pagination_class = CustomPageNumberPagination

    @swagger_auto_schema(
        operation_description="List all branches for a specific shop.",
        responses={200: BranchSerializer(many=True)},
    )
    def get_queryset(self):
        return Branch.objects.filter(is_active=True, shop__is_active=True)

    @swagger_auto_schema(
        operation_description="Create a new branch for a shop. Only the shop owner can create branches.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["address"],
            properties={
                "address": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Branch address"
                ),
                "latitude": openapi.Schema(
                    type=openapi.TYPE_NUMBER, description="Branch latitude (optional)"
                ),
                "longitude": openapi.Schema(
                    type=openapi.TYPE_NUMBER, description="Branch longitude (optional)"
                ),
            },
        ),
        responses={
            201: BranchSerializer,
            400: "Bad request",
        },
    )
    def perform_create(self, serializer):
        shop = Shop.objects.get(pk=self.kwargs["shop_pk"])

        if shop.owner != self.request.user:
            raise PermissionDenied(
                "You do not have permission to add a branch for this shop."
            )

        serializer.save(shop=shop)


class BranchListView(generics.ListAPIView):
    """
    get:
    List all active branches, optionally ordered by proximity to a given location.
    """

    serializer_class = BranchSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination

    @swagger_auto_schema(
        operation_description="List all active branches, "
        "optionally ordered by proximity to the given latitude and longitude.",
        manual_parameters=[
            openapi.Parameter(
                "latitude",
                openapi.IN_QUERY,
                type=openapi.TYPE_NUMBER,
                description="Latitude for location-based sorting",
            ),
            openapi.Parameter(
                "longitude",
                openapi.IN_QUERY,
                type=openapi.TYPE_NUMBER,
                description="Longitude for location-based sorting",
            ),
        ],
        responses={200: BranchSerializer(many=True)},
    )
    def get_queryset(self):
        queryset = Branch.objects.filter(is_active=True, shop__is_active=True)

        latitude = self.request.query_params.get("latitude")
        longitude = self.request.query_params.get("longitude")

        if latitude and longitude:
            try:
                latitude = float(latitude)
                longitude = float(longitude)
            except ValueError:
                return queryset

            # Haversine formula for calculating the distance
            distance_expression = ExpressionWrapper(
                ACos(
                    Sin(Radians(F("latitude"))) * Sin(Radians(latitude))
                    + Cos(Radians(F("latitude")))
                    * Cos(Radians(latitude))
                    * Cos(Radians(F("longitude")) - Radians(longitude))
                )
                * 6371,  # Radius of Earth in kilometers
                output_field=FloatField(),
            )

            # Annotate the queryset with the calculated distance and order by it
            queryset = queryset.annotate(distance=distance_expression).order_by(
                "distance"
            )

        return queryset
