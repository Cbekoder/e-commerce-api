from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status
from .serializers import AddToCartSerializer, CartItemPropertySerializer, CartItemSerializer, OrderSerializer, \
    OrderRetrieveSerializer, OrderListSerializer
from .models import CartItemProperty, CartItem, Coupon, Order


class AddToCartAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['product_id', 'count'],
            properties={
                'product_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'quantity': openapi.Schema(type=openapi.TYPE_INTEGER),
                'properties': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    additional_properties=openapi.Schema(type=openapi.TYPE_STRING)
                )
            }
        ),
        responses={
            201: "Item added to cart successfully",
            400: "Bad request - Invalid data provided",
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = AddToCartSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            cart_item = serializer.save(user=request.user)
            properties_json = CartItemPropertySerializer(CartItemProperty.objects.filter(cart_item=cart_item.id), many=True).data
            properties = {}
            for property in properties_json:
                properties[property['key']] = property['value']
            return Response({
                "message": "Product added to cart successfully.",
                "cart_item": {
                    "id": cart_item.id,
                    "user": cart_item.user.username,
                    "product": cart_item.product.title,
                    "count": cart_item.quantity,
                    "properties": properties
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CartItemDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        # Get product_id from query parameters
        product_id = request.query_params.get('product_id')

        try:
            # Ensure the cart item belongs to the authenticated user
            cart_item = CartItem.objects.get(product_id=product_id, user=request.user)
        except CartItem.DoesNotExist:
            return Response({"error": "CartItem not found"}, status=status.HTTP_404_NOT_FOUND)

        cart_item.delete()
        return Response({"message": "CartItem deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


class CartItemsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        coupon_code = request.headers.get('coupon-code')

        # Fetch all cart items for the user
        cart_items = CartItem.objects.filter(user=user)

        total_price = 0
        discounted_total_price = 0

        cart_items_data = []
        for cart_item in cart_items:
            product = cart_item.product

            subtotal = product.discount_price if product.discount_price is not None else product.price
            subtotal *= cart_item.quantity

            total_price += subtotal

            # Serialize product data with nested fields (pictures, properties)
            product_data = CartItemSerializer(product).data
            product_data['quantity'] = cart_item.quantity
            product_data['subtotal'] = subtotal

            cart_items_data.append(product_data)

        # Apply coupon discount if coupon code is provided and valid
        if coupon_code:
            try:
                coupon = Coupon.objects.get(code=coupon_code)
                discount_percent = coupon.discount_percent
                if discount_percent > 0:
                    discount_amount = total_price * (discount_percent / 100)
                    discounted_total_price = total_price - discount_amount
            except Coupon.DoesNotExist:
                pass  # Handle case where coupon doesn't exist

        # Prepare response data
        response_data = {
            'cart_items': cart_items_data,
            'total_price': total_price,
            'discounted_total_price': discounted_total_price
        }

        return Response(response_data, status=status.HTTP_200_OK)

class CreateOrderView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=OrderSerializer,
        responses={
            201: OrderSerializer,
            400: "Bad Request"
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = OrderSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            order = serializer.save()
            return Response(OrderSerializer(order).data, status=201)
        return Response(serializer.errors, status=400)

class OrderListView(ListAPIView):
    serializer_class = OrderListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Order.objects.filter(user=user).order_by('-datetime')

class OrderDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('order_id', openapi.IN_QUERY, description="Buyurtma ID raqami",
                              type=openapi.TYPE_INTEGER, required=True)
        ],
        responses={
            200: openapi.Response("Buyurtmalar ro'yxati", OrderRetrieveSerializer()),
            404: openapi.Response("Mahsulot topilmadi"),
        }
    )
    def get(self, request):
        user = self.request.user
        pk = self.request.query_params.get('order_id', None)
        queryset = Order.objects.filter(user=user)
        order = get_object_or_404(queryset, pk=pk)
        serializer = OrderRetrieveSerializer(order)
        return Response(serializer.data)







