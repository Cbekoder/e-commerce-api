from django.urls import path
from .views import *

urlpatterns = [
    path('my-wishlist/', WishlistProductsAPIView.as_view(), name='wishlist-products'),
    path('add-to-wishlist/', AddToWishlistAPIView.as_view(), name='add-to-wishlist'),
    path('remove-from-wishlist/', RemoveFromWishlistAPIView.as_view(), name='remove-from-wishlist'),
    path('submit-review/', SubmitReviewAPIView.as_view(), name='submit-review'),
    path('product-reviews/', ProductReviewsAPIView.as_view(), name='product-reviews'),
]