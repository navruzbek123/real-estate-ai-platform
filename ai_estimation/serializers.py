from rest_framework import serializers
from .models import AIEstimationHistory


class AIEstimationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIEstimationHistory
        fields = '__all__'


class AIEstimationInputSerializer(serializers.Serializer):
    area = serializers.IntegerField(min_value=1, max_value=10000)
    rooms = serializers.IntegerField(min_value=1, max_value=20)
    city = serializers.CharField(max_length=100)
    floor = serializers.IntegerField(min_value=1)
    total_floors = serializers.IntegerField(min_value=1)
    home_type = serializers.ChoiceField(choices=[
        ('Condo', 'Квартира'),
        ('House', 'Дом'),
        ('Townhouse', 'Таунхаус')
    ])
