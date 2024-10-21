from django.db import models

from shops.models import Shop


class Category(models.Model):
    """
    Category model which can have self-referencing categories for hierarchical structure.
    For example, 'Coffee' as parent and 'Cappuccino', 'Americano' as child categories.
    """

    name = models.CharField(max_length=255)
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="children"
    )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    """
    Product model to represent items in the shop.
    """

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to="products/images/", blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Base price
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name="products")
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self):
        return self.title


class OptionGroup(models.Model):
    """
    Represents a group of options for products.
    For example, an OptionGroup could be 'Milk' with options like 'Standard', 'Lactose-free'.
    """

    name = models.CharField(max_length=255)
    is_required = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Option(models.Model):
    """
    Represents individual options within an OptionGroup.
    For example, 'Lactose-free' in the 'Milk' OptionGroup.
    Each option can have a price adjustment.
    """

    group = models.ForeignKey(
        OptionGroup, on_delete=models.CASCADE, related_name="options"
    )
    name = models.CharField(max_length=255)
    price_adjustment = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.name} (+{self.price_adjustment})"


class ProductOption(models.Model):
    """
    Many-to-Many relationship between Product and OptionGroup.
    This allows each product to have different sets of OptionGroups.
    For example, a coffee product can have the 'Milk' and 'Coffee Bean Variety' options.
    """

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="product_options"
    )
    option_group = models.ForeignKey(OptionGroup, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.product.title} - {self.option_group.name}"
