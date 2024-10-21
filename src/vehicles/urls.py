from django.urls import path

from .views import (
    BrandDetailView,
    BrandListView,
    ColorDetailView,
    ColorListView,
    ModelDetailView,
    ModelListView,
    VehicleDetailView,
    VehicleListView,
)

urlpatterns = [
    path("brands/", BrandListView.as_view(), name="brand-list"),
    path("brands/<int:pk>/", BrandDetailView.as_view(), name="brand-detail"),
    path("brands/<int:pk>/models/", ModelListView.as_view(), name="model-list"),
    path("models/<int:pk>/", ModelDetailView.as_view(), name="model-detail"),
    path("colors/", ColorListView.as_view(), name="color-list"),
    path("colors/<int:pk>/", ColorDetailView.as_view(), name="color-detail"),
    path("vehicles/", VehicleListView.as_view(), name="vehicle-list"),
    path("vehicles/<int:pk>/", VehicleDetailView.as_view(), name="vehicle-detail"),
]
