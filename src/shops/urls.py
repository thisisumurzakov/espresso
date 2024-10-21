from django.urls import path

from .views import BranchListByShopIdCreateView, BranchListView, ShopListCreateView

urlpatterns = [
    path("shops/", ShopListCreateView.as_view(), name="shop-list"),
    path(
        "shops/<int:shop_pk>/branches/",
        BranchListByShopIdCreateView.as_view(),
        name="branch-list-create",
    ),
    path("branches/", BranchListView.as_view(), name="branch-list"),
]
