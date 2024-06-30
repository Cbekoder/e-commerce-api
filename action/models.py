from django.db import models
from product.models import Product
from user.models import Profile

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    stars = models.IntegerField()
    user = models.ForeignKey(Profile, on_delete=models.SET_NULL, blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Review by {self.user.email if self.user else "Anonymous"} on {self.product.title}'


class Wishlist(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f'{self.user.email} -> {self.product.title}'