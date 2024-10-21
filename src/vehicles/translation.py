from modeltranslation.decorators import register
from modeltranslation.translator import TranslationOptions

from .models import Brand, Color, Model


@register(Brand)
class BrandTranslationOptions(TranslationOptions):
    fields = ("name",)


@register(Model)
class ModelTranslationOptions(TranslationOptions):
    fields = ("name",)


@register(Color)
class ColorTranslationOptions(TranslationOptions):
    fields = ("name",)
