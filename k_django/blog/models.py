from django.db import models
from django.contrib.auth.models import User
from better_profanity import profanity
import string
from tinymce.models import HTMLField


def clean_text(text):
    translator = str.maketrans('', '', string.punctuation)
    return text.translate(translator).lower()

custom_bad_words = ["idiot", "freak", "jerk", "moron", "sucks", "bastard", "bitch", "asshole", "douche"]
profanity.load_censor_words(custom_words=custom_bad_words)

class Post(models.Model):
    DRAFT = 'draft'
    PUBLISHED = 'published'

    STATUS_CHOICES = [
        (DRAFT, 'Draft'),
        (PUBLISHED, 'Published'),
    ]

    title = models.CharField(max_length=200)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = HTMLField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=DRAFT)
    thumbnail = models.ImageField(upload_to='thumbnails/', blank=True, null=True)
    
    likes = models.ManyToManyField(User, through='Like', related_name='liked_posts', blank=True)
    bookmarks = models.ManyToManyField(User, related_name='bookmarked_posts', blank=True)
    
    verified = models.BooleanField(default=False)
    
    def total_likes(self):
        return self.likes.count()

    def total_bookmarks(self):
        return self.bookmarks.count()
    
    def __str__(self):
        return self.title
    
    def check_for_bad_words(self):
        cleaned_content = clean_text(self.content)
        return not profanity.contains_profanity(cleaned_content)

    def save(self, *args, **kwargs):
        self.verified = self.check_for_bad_words()
        super().save(*args, **kwargs)
    
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author} on {self.post}"

class Report(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='reports')
    reporter = models.ForeignKey(User, on_delete=models.CASCADE)
    reason = models.TextField()
    reported_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Report on {self.post.title} by {self.reporter.username}'


class PostView(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    ip_address = models.GenericIPAddressField()
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    viewed_on = models.DateField(auto_now_add=True)


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='likes_data')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')


class earning(models.Model):
    title = models.CharField(max_length=20)
    content = models.CharField(max_length=2000)
    link = models.URLField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add = True)
    
    def __str__(self):
        return self.title