from rest_framework import viewsets
from .models import Post  # Adjust if your model name is different
from .serializers import PostSerializer  # We'll create this next

class PostViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing blog posts.
    """
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer
