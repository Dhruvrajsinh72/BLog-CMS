from django.contrib import admin
from .models import Post
from .models import Report

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at', 'updated_at', 'status')
    list_filter = ('status', 'created_at', 'author')
    search_fields = ('title', 'author__username', 'content')
    ordering = ('-created_at',)
    actions = ['make_published']

    def make_published(self, request, queryset):
        updated_count = queryset.update(status='published')
        self.message_user(request, f'{updated_count} post(s) marked as published.')

    make_published.short_description = "Mark selected posts as published"

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('post', 'reporter', 'reported_at')