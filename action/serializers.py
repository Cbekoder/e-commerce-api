from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer, StringRelatedField
from product.serializers import ProductSerializer
from .models import Wishlist, Review

class WishlistSerializer(ModelSerializer):
    user = StringRelatedField(read_only=True)
    product = ProductSerializer(read_only=True)

    class Meta:
        model = Wishlist
        fields = ['user', 'product']


class ReviewSerializer(ModelSerializer):
    class Meta:
        model = Review
        fields = ['product', 'stars', 'comment', 'created_at']
        extra_kwargs = {
            'product': {'write_only': True},
            'created_at': {'read_only': True},
        }

    def validate_stars(self, value):
        if value < 1 or value > 5:
            raise ValidationError("Yulduzlar soni 1 dan 5 gacha bo'lishi kerak.")
        return value

