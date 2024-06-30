from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import *
from .serializers import WishlistSerializer, ReviewSerializer
from product.serializers import ProductSerializer

class AddToWishlistAPIView(APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'product_id',
                openapi.IN_QUERY,
                description="Qo'shiladigan mahsulot ID raqami",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={200: WishlistSerializer(many=True)}
    )
    def post(self, request, *args, **kwargs):
        product_id = request.query_params.get('product_id')

        if not product_id:
            return Response({"error": "Mahsulot ID raqami talab qilinadi."}, status=status.HTTP_400_BAD_REQUEST)
        product = get_object_or_404(Product, id=product_id)

        wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, product=product)
        if created:
            return Response({"message": "Mahsulot istaklar ro'yxatiga muvaffaqqiyatli qo'shildi."}, status=status.HTTP_201_CREATED)
        else:
            return Response({"message": "Mahsulot istaklar ro'yxatida allaqachon mavjud."}, status=status.HTTP_200_OK)


class RemoveFromWishlistAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'product_id',
                openapi.IN_QUERY,
                description="O'chiriladigan mahsulotning ID raqami",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={
            204: openapi.Response("Mahsulot istaklar ro'yxatidan o'chirildi"),
            404: openapi.Response("Mahsulot sizning istaklar ro'yxatingizda topilmadi yoki mavjud emas"),
            400: openapi.Response("Notog'ri so'rov")
        }
    )
    def delete(self, request, *args, **kwargs):
        product_id = request.query_params.get('product_id')

        if not product_id:
            return Response({"error": "Mahsulot ID raqami talab qilinadi"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Mahsulot topilmadi"}, status=status.HTTP_404_NOT_FOUND)

        user = request.user

        wishlist_item = Wishlist.objects.filter(user=user, product=product).first()

        if wishlist_item:
            wishlist_item.delete()
            return Response({"message": "Mahsulot istaklar ro'yxatidan o'chirildi"}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"error": "Mahsulot sizning istaklar ro'yxatingizda topilmadi"},
                            status=status.HTTP_404_NOT_FOUND)

class WishlistProductsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        responses={
            200: openapi.Response(
                description="User's wishlist products",
                examples={
                    "application/json": [
                        {
                            "id": 1,
                            "title": "Product Title",
                            "description": "Product Description",
                            "price": "123.45",
                            "discount_percent": 10,
                            "discount_price": "111.11",
                            "quantity": 5,
                            "review_quantity": 2,
                            "category": 1
                        },
                    ]
                }
            ),
            401: openapi.Response("User is not authenticated")
        }
    )
    def get(self, request, *args, **kwargs):
        user = request.user
        wishlist_items = Wishlist.objects.filter(user=user)
        products = [item.product for item in wishlist_items]

        # Serialize the products
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SubmitReviewAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=ReviewSerializer,
        responses={
            201: openapi.Response("Sharh muvaffaqiyatli qo'shildi"),
            400: openapi.Response("Notog'ri so'rov yoki validatsiya xatosi"),
            404: openapi.Response("Mahsulot topilmadi"),
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = ReviewSerializer(data=request.data)

        if serializer.is_valid():
            product_id = request.data.get('product')
            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                return Response({"error": "Mahsulot topilmadi"}, status=status.HTTP_404_NOT_FOUND)
            review = serializer.save(user=request.user, product=product)

            product.review_quantity += 1
            total_reviews = Review.objects.filter(product=product).count()
            total_stars = Review.objects.filter(product=product).aggregate(total=models.Sum('stars'))['total']
            product.stars = total_stars / total_reviews if total_reviews > 0 else 0

            product.save()

            return Response({
                "message": "Sharh muvaffaqiyatli qo'shildi",
                "review": ReviewSerializer(review).data
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProductReviewsAPIView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('product_id', openapi.IN_QUERY, description="Mahsulot ID raqami", type=openapi.TYPE_INTEGER, required=True)
        ],
        responses={
            200: openapi.Response("Sharhlar ro'yxati", ReviewSerializer(many=True)),
            404: openapi.Response("Mahsulot topilmadi"),
        }
    )
    def get(self, request, *args, **kwargs):
        product_id = request.query_params.get('product_id')

        if not product_id:
            return Response({"error": "Mahsulot ID raqami majburiy."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Mahsulot topilmadi"}, status=status.HTTP_404_NOT_FOUND)

        reviews = Review.objects.filter(product=product)
        serializer = ReviewSerializer(reviews, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)