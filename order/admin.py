from django.contrib import admin
from .models import *

# Admin customization for Cart model
@admin.register(CartItem)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product', 'quantity')
    search_fields = ('user__email', 'user__phone_number', 'product__title')
