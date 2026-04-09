from rest_framework import serializers
from .models import UserAccount, Notification, UserProfile


class UserAccountSerializer(serializers.ModelSerializer):
    role_display = serializers.CharField(source='get_role_display_name', read_only=True)

    class Meta:
        model = UserAccount
        fields = ['id', 'email', 'name', 'role', 'role_display', 'phone', 'avatar',
                 'bio', 'ai_estimations_today', 'ai_estimations_this_month',
                 'date_joined', 'last_login']
        read_only_fields = ['id', 'ai_estimations_today', 'ai_estimations_this_month', 'date_joined', 'last_login']


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ['id', 'user', 'notification_type', 'created_at']


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'


class SignupSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    password = serializers.CharField(min_length=6, write_only=True)
    password2 = serializers.CharField(min_length=6, write_only=True)

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({'password2': 'Пароли не совпадают'})
        if UserAccount.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({'email': 'Пользователь с таким email уже существует'})
        return data

    def create(self, validated_data):
        user = UserAccount.objects.create_user(
            email=validated_data['email'],
            name=validated_data['name'],
            password=validated_data['password']
        )
        return user
