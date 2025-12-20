# api/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Instruction, Ticket, UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['role', 'phone', 'department']


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile']


class InstructionSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)

    class Meta:
        model = Instruction
        fields = ['id', 'title', 'content', 'category', 'created_by', 'created_at', 'view_count', 'is_published']
        read_only_fields = ['created_by', 'created_at', 'view_count']


class TicketSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    assigned_to = UserSerializer(read_only=True)
    related_instruction = InstructionSerializer(read_only=True)

    class Meta:
        model = Ticket
        fields = [
            'id', 'title', 'description', 'status', 'priority', 'category',
            'created_by', 'assigned_to', 'created_at', 'updated_at', 'solution',
            'resolved_at', 'related_instruction'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at', 'resolved_at']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'first_name', 'last_name']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data.get('email', ''),
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        # Создаем профиль с ролью client по умолчанию
        UserProfile.objects.create(user=user, role='client')
        return user


# Дополнительные сериализаторы для создания/обновления
class TicketCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ['title', 'description', 'category', 'priority']


class InstructionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instruction
        fields = ['title', 'content', 'category', 'is_published']


class TicketUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ['status', 'solution', 'assigned_to', 'related_instruction']