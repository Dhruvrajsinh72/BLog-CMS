from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import report_post
from .views import manage_reports 
from blog.views import toggle_bookmark  
from django.shortcuts import redirect



urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('accounts/login/', lambda request: redirect('login')),
    path('home/', views.home, name='blog-home'),
    path('about/', views.about, name='blog-about'),
    path('manage-posts/', views.manage_posts, name='manage_posts'),
    path('add-post/', views.add_post, name='add_post'),
    path('update-post/<int:pk>/', views.update_post, name='update_post'),
    path('delete-post/<int:pk>/', views.delete_post, name='delete_post'),
    path('author/<int:author_id>/', views.author_posts, name='author_posts'),
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
    path('author/<int:author_id>/', views.filter_by_author, name='filter_by_author'),
    path('post/<int:post_id>/report/', report_post, name='report_post'),
    path('manage-reports/', manage_reports, name='manage_reports'),
    path('delete-report/<int:report_id>/', views.delete_report, name='delete_report'),
    path('post/<int:post_id>/like/', views.toggle_like, name='toggle_like'),
    path('toggle-bookmark/<int:post_id>/', views.toggle_bookmark, name='toggle_bookmark'),
    path('bookmarked-posts/', views.user_bookmarks, name='user_bookmarks'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('my-stats/', views.my_stats, name='my_stats'),
    path('earn/', views.earning_list, name='earning_list'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)