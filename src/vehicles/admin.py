from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from .models import Brand, Color, Model, Vehicle


@admin.register(Brand)
class BrandAdmin(TranslationAdmin):
    list_display = ("name", "user", "created_at", "updated_at")
    search_fields = ("name",)
    list_filter = ("user", "created_at")


@admin.register(Model)
class ModelAdmin(TranslationAdmin):
    list_display = ("name", "brand", "user", "created_at", "updated_at")
    search_fields = ("name", "brand__name")
    list_filter = ("brand", "user", "created_at")


@admin.register(Color)
class ColorAdmin(TranslationAdmin):
    list_display = ("name", "rgb_code", "user", "created_at", "updated_at")
    search_fields = ("name", "rgb_code")
    list_filter = ("user", "created_at")


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = (
        "plate_number",
        "brand",
        "model",
        "color",
        "user",
        "created_at",
        "updated_at",
    )
    search_fields = ("plate_number", "brand__name", "model__name", "color__name")
    list_filter = ("brand", "model", "color", "user", "created_at")
