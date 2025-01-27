from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from order.models import CartItem
from .serializers import *
from .models import *


class CategoriesAPIView(ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ProductsListAPIView(APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'category_id',
                openapi.IN_QUERY,
                description="ID of the category to filter products",
                type=openapi.TYPE_INTEGER
            )
        ],
        responses={200: ProductSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        category_id = request.query_params.get('category_id')

        if category_id is not None:
            category = get_object_or_404(Category, id=category_id)
            products = Product.objects.filter(category=category, is_deleted=False)
            serializer = ProductSerializer(products, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        products = Product.objects.filter(is_deleted=False)
        serializer = ProductSerializer(products, many=True)
        products_data = serializer.data

        if request.user.is_authenticated:
            wishlist_product_ids = set(Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True))
            cart_product_ids = set(CartItem.objects.filter(user=request.user).values_list('product_id', flat=True))
            for product in products_data:
                product['is_liked'] = product['id'] in wishlist_product_ids
                product['in_cart'] = product['id'] in cart_product_ids

        return Response(products_data, status=status.HTTP_200_OK)


class ProductDetailView(APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'product_id',
                openapi.IN_QUERY,
                description="Product ID majburiy",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={200: ProductDetailSerializer(many=True)}
    )
    def get(self, request):
        product_id = request.query_params.get('product_id')

        if not product_id:
            return Response({"error": "Mahsulot ID raqami majburiy."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProductDetailSerializer(product)
        return Response(serializer.data, status=status.HTTP_200_OK)
