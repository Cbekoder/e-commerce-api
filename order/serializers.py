from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from rest_framework.relations import StringRelatedField

from product.models import Product
from .models import CartItem, CartItemProperty, Order, Coupon, OrderDetail, OrderDetailProperty
from product.models import ProductProperty
from product.serializers import ProductSerializer, ProductPicturesSerializer, ProductPropertySerializer


class CartItemPropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItemProperty
        fields = ['key', 'value']


class AddToCartSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField()
    properties = serializers.DictField(child=serializers.CharField())

    def validate(self, attrs):
        product_id = attrs.get('product_id')
        properties = attrs.get('properties')

        # Check if product exists
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise serializers.ValidationError("Invalid product_id")

        # Validate each property in properties against ProductProperty entries
        for key, value in properties.items():
            try:
                # Check if the property key-value pair exists for the product
                ProductProperty.objects.get(product=product, key=key, value=value)
            except ProductProperty.DoesNotExist:
                raise serializers.ValidationError(
                    f"{product.title} mahsulot uchun noto'g'ri xususiyat (kalit so'z yoki qiymat) : {key}={value} for product ")

        return attrs

    def create(self, validated_data):
        properties_data = validated_data.pop('properties', None)

        cart_item = CartItem.objects.create(**validated_data)

        if properties_data:
            for key, value in properties_data.items():
                CartItemProperty.objects.create(cart_item=cart_item, key=key, value=value)

        return cart_item


class CartItemSerializer(serializers.ModelSerializer):
    pictures = ProductPicturesSerializer(many=True)
    properties = SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ('id', 'title', 'price', 'discount_price', 'quantity', 'pictures', 'properties')

    def to_representation(self, instance):
        subtotal = instance.discount_price if instance.discount_price is not None else instance.price
        subtotal *= instance.quantity

        return {
            'id': instance.id,
            'title': instance.title,
            'price': instance.price,
            'discount_price': instance.discount_price,
            'quantity': instance.quantity,
            'subtotal': subtotal,
            'pictures': ProductPicturesSerializer(instance.productpictures_set.filter(as_main=True), many=True).data,
            'properties': self.get_properties(instance.id)
        }

    def get_properties(self, obj):
        print(obj)
        properties = CartItemProperty.objects.filter(cart_item=obj)
        print(properties)
        grouped_properties = {}
        for prop in properties:
            if prop.key not in grouped_properties:
                grouped_properties[prop.key] = []
            grouped_properties[prop.key].append(prop.value)
        return grouped_properties


class OrderDetailPropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderDetailProperty
        fields = ['key', 'value']


class OrderDetailSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    properties = OrderDetailPropertySerializer(many=True, read_only=True)

    class Meta:
        model = OrderDetail
        fields = ['product', 'quantity', 'properties']


class OrderSerializer(serializers.ModelSerializer):
    order_details = OrderDetailSerializer(many=True, read_only=True)
    coupon_code = serializers.CharField(write_only=True, required=False)
    cart_item_ids = serializers.ListField(
        child=serializers.IntegerField(), write_only=True
    )

    class Meta:
        model = Order
        fields = [
            'company', 'street_address', 'apartment', 'city', 'phone', 'email',
            'paying_amount', 'payment_type', 'coupon_code', 'save_data', 'datetime',
            'order_details', 'cart_item_ids'
        ]

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user

        # Extract and process coupon code
        coupon_code = validated_data.pop('coupon_code', None)
        coupon = None
        discount_percent = 0

        if coupon_code:
            try:
                coupon = Coupon.objects.get(code=coupon_code)
                discount_percent = coupon.discount_percent
            except Coupon.DoesNotExist:
                raise serializers.ValidationError("Invalid coupon code")

        # Extract cart item IDs
        cart_item_ids = validated_data.pop('cart_item_ids', [])

        # Create the Order
        order = Order.objects.create(
            user=user,
            **validated_data,
            coupon=coupon
        )

        total_amount = 0

        for cart_item_id in cart_item_ids:
            try:
                cart_item = CartItem.objects.get(id=cart_item_id, user=user)
            except CartItem.DoesNotExist:
                continue

            product = cart_item.product
            quantity = cart_item.quantity
            price = product.discount_price if product.discount_price else product.price
            subtotal = price * quantity

            order_detail = OrderDetail.objects.create(
                order=order,
                product=product,
                quantity=quantity
            )

            cart_item_properties = cart_item.cartitemproperty_set.all()
            for prop in cart_item_properties:
                OrderDetailProperty.objects.create(
                    ordered_product=order_detail,
                    key=prop.key,
                    value=prop.value
                )

            total_amount += subtotal

        if discount_percent:
            total_amount -= total_amount * (discount_percent / 100)

        order.paying_amount = total_amount
        order.save()

        CartItem.objects.filter(id__in=cart_item_ids).delete()

        return order


class OrderListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'user', 'paying_amount', 'payment_type', 'datetime']


class OrderRetrieveSerializer(serializers.ModelSerializer):
    details = OrderDetailSerializer(source='orderdetail_set', many=True)

    class Meta:
        model = Order
        fields = [
            'id', 'company', 'street_address', 'apartment', 'city', 'phone',
            'email', 'paying_amount', 'payment_type', 'coupon', 'save_data',
            'datetime', 'details'
        ]
