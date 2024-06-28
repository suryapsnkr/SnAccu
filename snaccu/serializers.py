from rest_framework import serializers
from snaccu.models import User, Friend


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name']

class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User(
            first_name = validated_data['first_name'],
            last_name = validated_data['last_name'],
            email=validated_data['email'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
    
class LoginUserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length = 255)
    class Meta:
        model = User
        fields = ['email', 'password']
        # extra_kwargs = {'password': {'write_only': True}}

class QuerySerializer(serializers.ModelSerializer):
    query = serializers.CharField(max_length = 255)
    class Meta:
        model = User
        fields = ['query']
        extra_kwargs = {'password': {'write_only': True}}

class FRSerializer(serializers.ModelSerializer):
    class Meta:
        model = Friend
        fields = ['tuser']

class FASerializer(serializers.ModelSerializer):
    class Meta:
        model = Friend
        fields = ['fuser']

class FListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Friend
        field = ['first_name', 'last_name', 'email']