from django.conf import settings
from rest_framework import serializers
from users.models import User
from django.contrib.auth.hashers import make_password

class  UserSerializer(serializers.ModelSerializer):
    # payments=serializers.SerializerMethodField()

    class Meta:
        model= User
        fields = ["email", "password", "telegram_chat_id", "is_staff"]

    def create(self, validated_data):
        password = validated_data.pop("password")
        hash_password = make_password(password)
        validated_data["password"] = hash_password
        validated_data["is_active"]=False
        instance = User(**validated_data)
        instance.save()
        return instance



class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(min_length=8)

