from django.db import models

from user.models import Profile


class Category(models.Model):
    title = models.CharField(max_length=100)

    def __str__(self):
        return self.title

class Product(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    price = models.DecimalField( max_digits=12, decimal_places=2)
    discount_percent = models.IntegerField(null=True, blank=True)
    discount_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    quantity = models.IntegerField()
    review_quantity = models.IntegerField(default=0)
    stars = models.FloatField(default=0)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class ProductPictures(models.Model):
    file = models.ImageField(upload_to='product_photos')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    as_main = models.BooleanField(default=False)

    def __str__(self):
        return self.product.title

class ProductProperty(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    key = models.CharField(max_length=30)
    value = models.CharField(max_length=30)

    def __str__(self):
        return self.product.title + " -> " + self.key




