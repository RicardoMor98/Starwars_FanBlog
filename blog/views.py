from django.shortcuts import render, redirect, get_object_or_404
from django.views import generic
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from .models import Post, Comment, PostLike, PostView
from .forms import UserRegisterForm, CommentForm
from django.http import HttpResponseForbidden

# Home page view to display published posts
class PostList(generic.ListView):
    queryset = Post.objects.filter(status=1)  # Only published posts (status=1)
    template_name = "blog/index.html"  # Template for the home page
    paginate_by = 6  # Pagination: 6 posts per page

# About page view
class AboutPage(TemplateView):
    template_name = 'blog/about.html'

# User registration view
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()  # Save the new user
            username = form.cleaned_data.get('username')  # Get the username
            # Success message to inform the user their account was created
            messages.success(request, f'Account created for {username}! log in.')
            return redirect('login')  # Redirect to the login page
    else:
        form = UserRegisterForm()  # Instantiate an empty form
    # Render the registration form template
    return render(request, 'registration/register.html', {'form': form})

# User profile view
@login_required
def profile(request):
    user_posts = Post.objects.filter(author=request.user)
    user_comments = Comment.objects.filter(author=request.user)
    context = {
        'posts': user_posts,
        'post_count': user_posts.count(),  # Total number of posts
        'comments': user_comments,  # Comments made by the logged-in user
        'comment_count': user_comments.count(),  # Total number of comments
        'user': request.user,  # Logged-in user's details
    }

    # Render the profile page with additional data
    return render(request, 'blog/profile.html', context)

# Post Create View (for logged-in users)
class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'content', 'status']  # Fields included in the form
    template_name = 'blog/post_form.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        """Redirect to the profile page upon successful creation."""
        return reverse_lazy('profile')

# Post Update View (for logged-in users)
class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    fields = ['title', 'content', 'status']  # Fields to display in the form
    template_name = 'blog/post_form.html'

    def form_valid(self, form):
        if form.instance.author != self.request.user:
            messages.error(self.request, "You are not authorized to edit this post.")
            return redirect('profile')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('profile')

# Post Delete View (for logged-in users)
class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'blog/post_confirm_delete.html'

    def get_queryset(self):
        return super().get_queryset().filter(author=self.request.user)

    def get_success_url(self):
        messages.success(self.request, "Post deleted successfully!")
        return reverse_lazy('profile')

# Post Like functionality
@login_required
def post_like(request, pk):
    post = get_object_or_404(Post, pk=pk)

    # Ensure the user is authenticated
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to like or dislike a post.")
        return redirect('login')  # Redirect to login page if user is not authenticated

    existing_like = PostLike.objects.filter(post=post, user=request.user, like_type='like').first()
    existing_dislike = PostLike.objects.filter(post=post, user=request.user, like_type='dislike').first()

    if 'like' in request.POST:
        if existing_like:
            existing_like.delete()
            messages.success(request, f"You've unliked the post: {post.title}")
        else:
            if existing_dislike:
                existing_dislike.delete()
                messages.success(request, f"You've removed your dislike on the post: {post.title}")
            PostLike.objects.create(post=post, user=request.user, like_type='like')
            messages.success(request, f"You've liked the post: {post.title}")

    elif 'dislike' in request.POST:
        if existing_dislike:
            existing_dislike.delete()
            messages.success(request, f"You've removed your dislike on the post: {post.title}")
        else:
            if existing_like:
                existing_like.delete()
                messages.success(request, f"You've unliked the post: {post.title}")
            PostLike.objects.create(post=post, user=request.user, like_type='dislike')
            messages.success(request, f"You've disliked the post: {post.title}")

    return redirect('post_detail', pk=post.pk)

# Post Detail View (with likes and views)
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post = track_post_view(request, pk)

    comments = post.comments.filter(approved=True)
    new_comment = None
    next_url = request.GET.get('next', '/')

    # Check if the user has liked or disliked the post
    user_has_liked = PostLike.objects.filter(post=post, user=request.user, like_type='like').exists() if request.user.is_authenticated else False
    user_has_disliked = PostLike.objects.filter(post=post, user=request.user, like_type='dislike').exists() if request.user.is_authenticated else False

    if request.method == "POST":
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.author = request.user
            new_comment.save()
            messages.success(request, "Your comment has been submitted for review.")
            return redirect("post_detail", pk=post.pk)
    else:
        comment_form = CommentForm()

    return render(request, 'blog/post_detail.html', {
        'post': post,
        'comments': comments,
        'new_comment': new_comment,
        'comment_form': comment_form,
        'next_url': next_url,
        'user_has_liked': user_has_liked,
        'user_has_disliked': user_has_disliked,
    })

# Edit comment view
def edit_comment(request, id):
    comment = get_object_or_404(Comment, id=id)

    if comment.author != request.user:
        return HttpResponseForbidden("You are not allowed to edit this comment.")

    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('post_detail', pk=comment.post.id)
    else:
        form = CommentForm(instance=comment)

    return render(request, 'blog/edit_comment.html', {'form': form, 'comment': comment})

# Delete comment view
def delete_comment(request, id):
    comment = get_object_or_404(Comment, id=id)

    if comment.author != request.user:
        return HttpResponseForbidden("You are not allowed to delete this comment.")

    comment.delete()
    return redirect('post_detail', pk=comment.post.id)

# Track the post view with the user's IP address
def track_post_view(request, pk):
    post = get_object_or_404(Post, pk=pk)
    ip_address = request.META.get('REMOTE_ADDR')

    if not PostView.objects.filter(post=post, ip_address=ip_address).exists():
        PostView.objects.create(post=post, ip_address=ip_address)
        post.increment_view_count()

    return post
