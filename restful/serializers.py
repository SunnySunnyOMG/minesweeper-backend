from rest_framework import serializers
from .models import Game
from django.contrib.auth.models import User
from .helpers import gen_map_data


# Serializers define the API representation.

class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        exclude = ('map_data',)
        read_only_fields = ['created_at', 'updated_at', 'map_data']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')

class SignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password','email', 'first_name', 'last_name')

