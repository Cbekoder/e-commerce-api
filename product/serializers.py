from rest_framework.serializers import ModelSerializer, SerializerMethodField

from action.models import Wishlist
from .models import Category, Product, ProductPictures, ProductProperty


class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'title']


class ProductPicturesSerializer(ModelSerializer):
    class Meta:
        model = ProductPictures
        fields = ['file', 'as_main']


class ProductPropertySerializer(ModelSerializer):
    class Meta:
        model = ProductProperty
        fields = ['key', 'value']


class ProductSerializer(ModelSerializer):
    pictures = SerializerMethodField()
    is_liked = SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'title', 'price', 'discount_percent', 'discount_price', 'review_quantity', 'stars', 'is_liked',
                  'pictures']

    def get_pictures(self, obj):
        pictures = obj.productpictures_set.all()
        sorted_pictures = sorted(pictures, key=lambda x: not x.as_main)
        return [picture.file.url for picture in sorted_pictures]

    def get_is_liked(self, obj):
        request = self.context.get('request', None)
        if request and hasattr(request, 'user'):
            return Wishlist.objects.filter(user=request.user, product=obj).exists()
        return False

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['is_liked'] = self.get_is_liked(instance)
        return representation


class ProductDetailSerializer(ModelSerializer):
    pictures = SerializerMethodField()
    properties = SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'category', 'price', 'discount_percent', 'discount_price', 'quantity',
                  'stars', 'review_quantity', 'pictures', 'properties']

    def get_pictures(self, obj):
        pictures = obj.productpictures_set.all()
        sorted_pictures = sorted(pictures, key=lambda x: not x.as_main)
        return ProductPicturesSerializer(sorted_pictures, many=True).data

    def get_properties(self, obj):
        properties = obj.productproperty_set.all()
        grouped_properties = {}
        for prop in properties:
            if prop.key not in grouped_properties:
                grouped_properties[prop.key] = []
            grouped_properties[prop.key].append(prop.value)
        return grouped_properties
