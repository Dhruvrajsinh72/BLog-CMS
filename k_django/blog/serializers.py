from rest_framework import serializers
from .models import Post  # Replace with your actual model names

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'
