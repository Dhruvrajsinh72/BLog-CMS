from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from django.contrib.admin.views.decorators import staff_member_required

from django.http import JsonResponse, HttpResponse, HttpResponseForbidden
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q

from users.models import Profile 
from .models import Post
from .models import Post, User
from .forms import PostForm
from django.template.loader import render_to_string

from .models import Post, Report
from .forms import ReportForm

from .models import Post, Comment
from .forms import CommentForm
from .models import Report 

from django.utils.timezone import localtime
from django.urls import reverse

from django.views.decorators.http import require_POST

from .models import Post, PostView
from django.utils import timezone
from datetime import timedelta
from django.utils.timezone import now

from .models import earning
from .models import Like


def landing_page(request):
    if request.user.is_authenticated:
        return redirect('blog-home')  # name of your blog homepage URL
    return render(request, 'blog/landing.html')


def home(request):
    query = request.GET.get('q', '')
    author_id = request.GET.get('author', '')

    
    posts = Post.objects.filter(status='published',verified=True).order_by('-created_at')

    if query:
        posts = posts.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(author__username__icontains=query) |
            Q(created_at__icontains=query)
        )

    if author_id:
        posts = posts.filter(author_id=author_id)

    paginator = Paginator(posts, 4)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    authors = User.objects.filter(post__status='published').distinct()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        html = render_to_string('blog/filtered_posts.html', {'page_obj': page_obj})
        pagination_html = render_to_string('blog/pagination.html', {'page_obj': page_obj})
        return JsonResponse({'html': html, 'pagination': pagination_html})

    return render(request, 'blog/home.html', {
        'page_obj': page_obj,
        'authors': authors,
        'query': query,
        'author_id': author_id
    })



def about(request):
    return render(request, 'blog/about.html')



@login_required
def manage_posts(request):
    if request.user.is_superuser:
        posts = Post.objects.all().order_by('-created_at')  # Superuser sees all posts
    else:
        posts = Post.objects.filter(author=request.user).order_by('-created_at')
    paginator = Paginator(posts, 7)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        html = render_to_string('blog/manage_posts_list.html', {'page_obj': page_obj}, request)
        pagination_html = render_to_string('blog/pagination.html', {'page_obj': page_obj}, request)
        return JsonResponse({'html': html, 'pagination': pagination_html})  #  Sends only required parts

    return render(request, 'blog/manage_posts.html', {'page_obj': page_obj})



    
@login_required
def add_post(request):
    """
    Allows users to create a new blog post.
    """
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, "Post added successfully!")
            return redirect('manage_posts')
        else:
            messages.error(request, "Error adding post. Please check the form.")
    else:
        form = PostForm()
    
    return render(request, 'blog/add_post.html', {'form': form, "hide_sidebar": True,})

@login_required
def update_post(request, pk):
    """
    Allows users to update an existing blog post.
    """
    post = get_object_or_404(Post, pk=pk)

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, "Post updated successfully!")
            return redirect('manage_posts')
        else:
            messages.error(request, "Error updating post. Please check the form.")
    else:
        form = PostForm(instance=post)

    return render(request, 'blog/update_post.html', {'form': form})

@login_required
def delete_post(request, pk):
    """
    Allows users to delete their own posts. Admins can delete any post.
    """
    post = get_object_or_404(Post, pk=pk)

    if post.author != request.user and not request.user.is_superuser:
        return HttpResponseForbidden("You are not allowed to delete this post.")

    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Post deleted successfully!')
        return redirect('manage_posts')
    
    return HttpResponse(status=405)


def sidebar_context(request):
    """
    Provides context data for the sidebar including latest posts, authors, and search results.
    """
    latest_posts = Post.objects.filter(status='published').order_by('-created_at')[:5]
    authors = User.objects.filter(post__status='published').distinct()

    query = request.GET.get('q')
    search_results = None
    if query:
        search_results = Post.objects.filter(
            Q(title__icontains=query) | Q(content__icontains=query),
            status='published'
        )[:5]  # Limit search results

    return {
        'latest_posts': latest_posts,
        'authors': authors,
        'search_results': search_results,
    }

def author_posts(request, author_id):
    """
    Displays all posts by a specific author.
    """
    author = get_object_or_404(User, id=author_id)
    posts = Post.objects.filter(author=author, status='published').order_by('-created_at')

    return render(request, 'blog/author_posts.html', {'posts': posts, 'author': author})

def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    comments = post.comments.all().order_by("-created_at")

    # Get visitor IP
    ip = get_client_ip(request)
    user = request.user if request.user.is_authenticated else None
    today = now().date()

    # Check if this IP has already viewed this post today
    if not PostView.objects.filter(post=post, ip_address=ip, user=user, viewed_on=now().date()).exists():
        PostView.objects.create(post=post, ip_address=ip, user=user)
        
    if request.method == "POST":
        if request.user.is_authenticated:
            form = CommentForm(request.POST)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.post = post
                comment.author = request.user
                comment.save()

                # ✅ AJAX request handling
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({
                        "success": True,
                        "author": comment.author.username,
                        "author_url": reverse("user_profile", args=[comment.author.username, post.pk]),
                        "created_at": localtime(comment.created_at).strftime('%b %d, %Y %I:%M %p'),
                        "content": comment.content,
                        "comment_id": comment.id,
                        "can_delete": comment.author == request.user,
                    })

                # Fallback for regular form post
                messages.success(request, "Your comment has been added!")
                return redirect("post_detail", pk=post.pk)
            else:
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({"success": False, "error": "Invalid form data."})
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({"success": False, "error": "You must be logged in to comment."})
            messages.error(request, "You must be logged in to comment.")
            return redirect("login")
    else:
        form = CommentForm()

    return render(request, "blog/post_detail.html", {
        "post": post,
        "comments": comments,
        "form": form,
        "post_id": post.pk
    })

@require_POST
def delete_comment(request, comment_id):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            comment = Comment.objects.get(id=comment_id)
            
            if comment.author == request.user or comment.post.author == request.user:
                comment.delete()
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'error': 'You are not authorized to delete this comment.'}, status=403)
        except Comment.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Comment does not exist.'}, status=404)
    return JsonResponse({'success': False, 'error': 'Invalid request.'}, status=400)


def filter_by_author(request, author_id):
    """
    Filters posts by a specific author and returns a partial HTML update.
    """
    author = get_object_or_404(User, id=author_id)
    posts = Post.objects.filter(author=author, status='published').order_by('-created_at')

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        html = render_to_string('blog/filtered_posts.html', {'posts': posts, 'author': author})
        return JsonResponse({'html': html})

    return render(request, 'blog/author_posts.html', {'posts': posts, 'author': author})


@login_required
def report_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    # Prevent duplicate reports by the same user
    if Report.objects.filter(post=post, reporter=request.user).exists():
        messages.warning(request, "You have already reported this post.")
        return redirect('post_detail', pk=post.id)


    if request.method == "POST":
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.post = post
            report.reporter = request.user
            report.save()
            
            # Hide the post if it gets more than 3 reports
            if post.reports.count() > 3:
                post.is_active = False
                post.save()
            
            messages.success(request, "Your report has been submitted.")
            return redirect('post_detail', pk=post.id)
    else:
        form = ReportForm()

    return render(request, 'blog/report_post.html', {'form': form, 'post': post, 'hide_sidebar': True, 'page_title': 'Report Post'})

@staff_member_required
def manage_reports(request):
    reports_list = Report.objects.all().order_by('-reported_at')  #  Define reports_list correctly
    paginator = Paginator(reports_list, 6)  #  Paginate reports (10 per page)
    
    page_number = request.GET.get('page')  #  Get the requested page number
    reports = paginator.get_page(page_number)  #  Fetch reports for the requested page
    
    return render(request, 'blog/manage_reports.html', {'reports': reports})

def delete_report(request, report_id):
    """Admin can dismiss a report without deleting the post."""
    report = get_object_or_404(Report, id=report_id)
    report.delete()
    return redirect('manage_reports')


@login_required
def toggle_like(request, post_id):
    post = Post.objects.get(pk=post_id)
    user = request.user
    liked = False
    if user in post.likes.all():
        post.likes.remove(user)
    else:
        post.likes.add(user)
        liked = True
    return JsonResponse({'liked': liked, 'likes_count': post.likes.count()})

@login_required
def toggle_bookmark(request, post_id):
    post = Post.objects.get(pk=post_id)
    user = request.user
    bookmarked = False
    if post in user.profile.bookmarks.all():
        user.profile.bookmarks.remove(post)
    else:
        user.profile.bookmarks.add(post)
        bookmarked = True
    return JsonResponse({'bookmarked': bookmarked})

@login_required
def user_bookmarks(request):
    user = request.user
    bookmarked_posts = user.profile.bookmarks.all()
    return render(request, 'blog/user_bookmarks.html', {'bookmarked_posts': bookmarked_posts})



@login_required
def my_stats(request):
    user = request.user
    posts = Post.objects.filter(author=user)
    post_ids = posts.values_list('id', flat=True)

    today = timezone.now().date()
    last_7_days = [today - timedelta(days=i) for i in range(6, -1, -1)]
    date_labels = [day.strftime('%d %b').lstrip('0') for day in last_7_days]

    daily_views = []
    daily_likes = []

    for day in last_7_days:
        view_count = PostView.objects.filter(post__in=post_ids, viewed_on=day).count()
        like_count = Like.objects.filter(post__in=post_ids, created_at__date=day).count()

        daily_views.append(view_count)
        daily_likes.append(like_count)

    total_views = PostView.objects.filter(post__in=post_ids).count()

    context = {
        'labels': date_labels,
        'views': daily_views,
        'likes': daily_likes,
        'total_views': total_views,
        'posts': posts,
    }
    return render(request, 'blog/stats.html', context)


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def earning_list(request):
    pages = earning.objects.all()
    return render(request, 'blog/earning_list.html', {'pages': pages})
