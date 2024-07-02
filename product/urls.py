from django.urls import path
from .views import *

urlpatterns = [
    path('categories/', CategoriesAPIView.as_view()),
    path('list/', ProductsListAPIView.as_view(), name='products-list'),
    path('detail/', ProductDetailView.as_view(), name='products-detail'),
]