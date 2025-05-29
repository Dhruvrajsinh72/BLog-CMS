# users/views_api.py

from django.contrib.auth.models import User
from rest_framework import viewsets
from .serializers import UserSerializer

class UserViewSet(viewsets.ReadOnlyModelViewSet):  # Use full ModelViewSet if you want to allow edits
    queryset = User.objects.all()
    serializer_class = UserSerializer
