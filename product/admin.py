from django.contrib import admin
from .models import Category, Product, ProductPictures, ProductProperty

# # Customizing the display for the Profile model
# @admin.register(Profile)
# class ProfileAdmin(admin.ModelAdmin):
#     list_display = ('id', 'email', 'phone_number', 'first_name', 'last_name', 'is_active', 'is_staff')
#     search_fields = ('email', 'phone_number', 'first_name', 'last_name')
#     list_filter = ('is_active', 'is_staff', 'is_superuser')
#     ordering = ('email',)

# Admin customization for Category model
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')
    search_fields = ('title',)

# Inline for displaying ProductPictures within the Product admin
class ProductPicturesInline(admin.TabularInline):
    model = ProductPictures
    extra = 1

# Inline for displaying ProductProperty within the Product admin
class ProductPropertyInline(admin.TabularInline):
    model = ProductProperty
    extra = 1

# Admin customization for Product model
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'category', 'price', 'discount_percent', 'discount_price', 'quantity', 'review_quantity', 'is_deleted')
    search_fields = ('title', 'category__title')
    list_filter = ('category', 'is_deleted', 'discount_percent')
    inlines = [ProductPicturesInline, ProductPropertyInline]
    fieldsets = (
        (None, {'fields': ('title', 'description', 'category', 'price', 'quantity', 'is_deleted')}),
        ('Discount Information', {'fields': ('discount_percent', 'discount_price')}),
    )

# Admin customization for ProductPictures model
@admin.register(ProductPictures)
class ProductPicturesAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'file', 'as_main')
    search_fields = ('product__title',)
    list_filter = ('as_main',)

# Admin customization for ProductProperty model
@admin.register(ProductProperty)
class ProductPropertyAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'key', 'value')
    search_fields = ('product__title', 'key', 'value')
    list_filter = ('key',)

