from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout
from django.contrib import messages
from .forms import UserRegistrationForm, ProfileUpdateForm
from django.http import JsonResponse
import json
from django.contrib.auth.models import User
from blog.models import Post
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from .models import Profile
from django.views.decorators.http import require_POST
from django.urls import reverse_lazy

from django.core.mail import send_mail
from .forms import ContactForm

# User Registration View
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)  # Include request.FILES
        if form.is_valid():
            user = form.save()
            profile_picture = form.cleaned_data.get('profile_picture')

            # Create or update the Profile
            profile, created = Profile.objects.get_or_create(user=user)
            if profile_picture:
                profile.profile_picture = profile_picture
            profile.save()

            messages.success(request, 'Registration successful! Please log in.')
            return redirect('login')
    else:
        form = UserRegistrationForm()

    return render(request, 'users/register.html', {'form': form})


# Profile View
@login_required
def profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    user_form = UserRegistrationForm(instance=request.user)
    profile_form = ProfileUpdateForm(instance=profile)
    posts = Post.objects.filter(author=request.user).order_by('-created_at')

    if request.method == 'POST':
        # ✅ If "Remove Profile" button is clicked
        if 'remove_profile_picture' in request.POST:
        
            if profile.profile_picture and profile.profile_picture.name != 'media/default-profile.jpg':
                profile.profile_picture.delete(save=False)
                profile.profile_picture = 'media/default-profile.jpg'
                profile.save()
                messages.success(request, 'Profile picture removed successfully.')
            return redirect('profile')

        # ✅ If "Update" button is clicked
        if 'update_profile_picture' in request.POST:
            user_form = UserRegistrationForm(request.POST, instance=request.user)
            profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)

            if user_form.is_valid() and profile_form.is_valid():
                user_form.save()
                profile_form.save()
                messages.success(request, 'Your profile has been updated successfully!')
                return redirect('profile')

    return render(request, 'users/profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'profile': profile,
        'profile_user': request.user,
        'posts': posts,
        'own_profile': True,
        'followers': profile.followers.all(),
        'following': [p.user for p in request.user.following.all()],
    })


@login_required
def profile_update(request):
    user = request.user
    profile = user.profile

    if request.method == "POST":
        if request.content_type == 'application/json':
            body = json.loads(request.body)
            if body.get('remove_profile_picture'):
                if profile.profile_picture and profile.profile_picture.name != 'default-profile.jpg':
                    profile.profile_picture.delete(save=False)
                    profile.profile_picture = 'default-profile.jpg'
                    profile.save()
                    return JsonResponse({
                        "success": True,
                        "profile_picture_url": profile.profile_picture.url
                    })
                return JsonResponse({"success": False, "error": "No custom profile picture to remove."})
        else:
            user.first_name = request.POST.get("first_name", "")
            user.last_name = request.POST.get("last_name", "")
            user.email = request.POST.get("email", "")
            user.save()

            profile.bio = request.POST.get("bio", "")
            if "profile_picture" in request.FILES:
                profile.profile_picture = request.FILES["profile_picture"]
            profile.save()

            return JsonResponse({
                "success": True,
                "profile_picture_url": profile.profile_picture.url if profile.profile_picture else None
            })

    return JsonResponse({"success": False, "error": "Invalid request"})

# Logout View
def logout(request):
    auth_logout(request)
    return redirect(reverse_lazy('landing'))

def user_profile(request, username, id):
    """ Show another user's profile and their posts """
    profile_user = get_object_or_404(User, username=username)
    profile = get_object_or_404(Profile, user=profile_user)  # Get the correct profile
    posts = Post.objects.filter(author=profile_user).order_by('-created_at')

    return render(request, 'users/user_profile.html', {  # ✅ Using the new template
        'profile_user': profile_user,  # ✅ Pass the correct user
        'profile': profile,  # ✅ Pass the correct profile
        'posts': posts,
        'post_id':id,
    })


@require_POST
@login_required
def follow_unfollow(request, username, post_id):
    target_user = get_object_or_404(User, username=username)
    target_profile = get_object_or_404(Profile, user=target_user)
    current_user = request.user

    following = False

    if current_user != target_user:
        if current_user in target_profile.followers.all():
            target_profile.followers.remove(current_user)
        else:
            target_profile.followers.add(current_user)
            following = True

    # Return updated counts and follow status
    return JsonResponse({
        'following': following,
        'follower_count': target_profile.followers.count(),
        'following_count': target_user.following.count()
    })

def search_users(request):
    query = request.GET.get('q', '')
    users = User.objects.filter(username__icontains=query) if query else []
    
    return render(request, 'users/search_results.html', {'users': users, 'query': query})

@csrf_exempt
def user_autocomplete(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        term = request.GET.get('term', '')
        users = User.objects.filter(username__icontains=term)[:5]
        usernames = list(users.values_list('username', flat=True))
        return JsonResponse(usernames, safe=False)
    return JsonResponse([], safe=False)

def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']

            # Send an email
            send_mail(
                f"New Contact: {subject}",
                f"From {name} <{email}>\n\nMessage:\n{message}",
                email,  # from email
                ['youradminemail@example.com'],  # your admin email
            )

            return redirect('contact_success')
    else:
        form = ContactForm()
    return render(request, 'contact.html', {'form': form})

def contact_success_view(request):
    return render(request, 'contact_success.html')