from django.db import models
from product.models import Product
from user.models import Profile

class Coupon(models.Model):
    code = models.CharField(max_length=10)
    discount_percent = models.IntegerField()


class CartItem(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()

    # def __str__(self):
    #     return self.user.email+" -> "+self.product.title

class CartItemProperty(models.Model):
    cart_item = models.ForeignKey(CartItem, on_delete=models.CASCADE)
    key = models.CharField(max_length=30)
    value = models.CharField(max_length=30)

    def __str__(self):
        return self.cart_item.product.title+" -> "+self.key


class Order(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    company = models.CharField(max_length=60, null=True, blank=True)
    street_address = models.CharField(max_length=50)
    apartment = models.CharField(max_length=50, null=True, blank=True)
    city = models.CharField(max_length=30)
    phone = models.CharField(max_length=13)
    email = models.EmailField()
    paying_amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_type = models.CharField(max_length=20)
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    save_data = models.BooleanField(default=False)
    datetime = models.DateTimeField(auto_now_add=True)

class OrderDetail(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()

class OrderDetailProperty(models.Model):
    ordered_product = models.ForeignKey(OrderDetail, on_delete=models.CASCADE)
    key = models.CharField(max_length=30)
    value = models.CharField(max_length=30)

    def __str__(self):
        return self.ordered_product.product.title, ' -> ', self.key


