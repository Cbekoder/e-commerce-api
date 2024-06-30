from django.contrib import admin
from .models import *

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'stars', 'user')
    search_fields = ('product__title', 'user__email', 'user__phone_number')
    list_filter = ('stars',)

# Admin customization for Wishlist model
@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product')
    search_fields = ('user__email', 'user__phone_number', 'product__title')

