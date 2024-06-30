from django.urls import path
from .views import *

urlpatterns = [
    path("add-to-cart/", AddToCartAPIView.as_view(), name='add-to-cart'),
    path('remove-from-cart', CartItemDeleteView.as_view(), name='remove-cart-item'),
    path('cart-items/', CartItemsAPIView.as_view(), name='cart-items'),
    path('create/', CreateOrderView.as_view(), name='create_order'),
    path('list/', OrderListView.as_view(), name='order_list'),
    path('detail/', OrderDetailView.as_view(), name='order_detail'),
]