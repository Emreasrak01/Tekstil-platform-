from django.conf import settings
from django.db import models

from products.models import Product


class Favorite(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favorites',
        limit_choices_to={'user_type': 'store'},
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Favori'
        verbose_name_plural = 'Favoriler'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['user', 'product'], name='unique_store_favorite')
        ]

    def __str__(self):
        return f'{self.user} - {self.product}'


class CartItem(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cart_items',
        limit_choices_to={'user_type': 'store'},
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='cart_items')
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Sepet Ürünü'
        verbose_name_plural = 'Sepet Ürünleri'
        ordering = ['-updated_at']
        constraints = [
            models.UniqueConstraint(fields=['user', 'product'], name='unique_store_cart_item')
        ]

    @property
    def line_total(self):
        return self.product.price * self.quantity

    def __str__(self):
        return f'{self.product} x {self.quantity}'
