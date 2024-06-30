from django.urls import path
from .views import *

urlpatterns = [
    path('categories/', CategoriesAPIView.as_view()),
    path('list-by-category/', ProductsByCategoryAPIView.as_view(), name='products-by-category'),
    path('detail/', ProductDetailView.as_view(), name='products-detail'),
]