from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .serializers import *
from .models import *

class CategoriesAPIView(ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class ProductsByCategoryAPIView(APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'category_id',
                openapi.IN_QUERY,
                description="ID of the category to filter products",
                type=openapi.TYPE_INTEGER,
                required=True  # This makes the parameter required
            )
        ],
        responses={200: ProductSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        category_id = request.query_params.get('category_id')

        if not category_id:
            return Response({"error": "Category ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return Response({"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND)

        products = Product.objects.filter(category=category, is_deleted=False)
        serializer = ProductSerializer(products, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

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

