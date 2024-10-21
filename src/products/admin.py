from django.contrib import admin

from .models import Category, Option, OptionGroup, Product, ProductOption


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "parent", "is_active")
    list_filter = ("is_active", "parent")
    search_fields = ("name",)
    ordering = ("name",)


class ProductOptionInline(admin.TabularInline):
    model = ProductOption
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("title", "shop", "category", "price")
    list_filter = ("shop", "category")
    search_fields = ("title", "description")
    inlines = [ProductOptionInline]
    ordering = ("title",)


class OptionInline(admin.TabularInline):
    model = Option
    extra = 1


@admin.register(OptionGroup)
class OptionGroupAdmin(admin.ModelAdmin):
    list_display = ("name", "is_required")
    search_fields = ("name",)
    inlines = [OptionInline]
    ordering = ("name",)


@admin.register(Option)
class OptionAdmin(admin.ModelAdmin):
    list_display = ("name", "group", "price_adjustment")
    list_filter = ("group",)
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(ProductOption)
class ProductOptionAdmin(admin.ModelAdmin):
    list_display = ("product", "option_group")
    list_filter = ("product__shop", "option_group")
    search_fields = ("product__title", "option_group__name")
    ordering = ("product",)
