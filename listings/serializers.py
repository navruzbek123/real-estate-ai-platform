from rest_framework import serializers
from .models import Listing


class ListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Listing
        fields = ['id', 'title', 'slug', 'address', 'city', 'state', 'price',
                 'bedrooms', 'bathrooms', 'sqft', 'photo_main', 'home_type', 'is_premium']
        read_only_fields = ['id']


class ListingDetailSerializer(serializers.ModelSerializer):
    realtor_name = serializers.CharField(source='realtor.name', read_only=True)
    photo_count = serializers.SerializerMethodField()

    class Meta:
        model = Listing
        fields = '__all__'
        lookup_field = 'slug'

    def get_photo_count(self, obj):
        return obj.get_photo_count()


class ListingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Listing
        fields = ['title', 'address', 'city', 'state', 'zipcode', 'description',
                 'sale_type', 'price', 'bedrooms', 'bathrooms', 'home_type', 'sqft',
                 'photo_main', 'is_published']
