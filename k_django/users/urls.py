from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from .views import user_profile
from .views import profile
from .views import search_users
from .views import user_autocomplete


urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', views.logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('profile/update/', views.profile_update, name='profile_update'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('profile/', profile, name='profile'),  # Logged-in user's profile
    path('profile/<str:username>/<int:id>/', views.user_profile, name='user_profile'),
    path('profile/<str:username>/follow/<int:post_id>/', views.follow_unfollow, name='follow_unfollow'),
    path('search-users/', search_users, name='search_users'),
    path('autocomplete/', user_autocomplete, name='user_autocomplete'),
    path('contact/', views.contact_view, name='contact'),
    path('contact-success/', views.contact_success_view, name='contact_success'),
]

if settings.DEBUG:  # Serve media files only in development mode
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)