from django.contrib import admin

from .models import Branch, Shop


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ("name", "owner")


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ("shop", "address")
