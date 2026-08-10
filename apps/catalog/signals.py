from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Product, ProductVariant


@receiver(post_save, sender=ProductVariant)
def refresh_product_search_text(sender, instance: ProductVariant, **kwargs):
    product = instance.product
    product.rebuild_search_text()
    Product.objects.filter(pk=product.pk).update(search_text=product.search_text)
