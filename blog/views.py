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
    # Fetch only posts and comments created by the logged-in user
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


class PostCreateView(LoginRequiredMixin, CreateView):
    """
    View to handle the creation of a new blog post.
    Assigns the logged-in user as the author automatically.
    """
    model = Post
    fields = ['title', 'content', 'status']  # Fields included in the form
    template_name = 'blog/post_form.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        """Redirect to the profile page upon successful creation."""
        return reverse_lazy('profile')


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    fields = ['title', 'content', 'status']  # Fields to display in the form
    template_name = 'blog/post_form.html'

    def form_valid(self, form):
        # Ensure the post being updated belongs to the logged-in user
        if form.instance.author != self.request.user:
            messages.error(self.request, "You are not authorized to edit this post.")
            return redirect('profile')
        return super().form_valid(form)

    def get_success_url(self):
        # Redirect to the profile page after a successful update
        return reverse_lazy('profile')


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'blog/post_confirm_delete.html'

    def get_queryset(self):
        # Ensure the user can only delete their own posts
        queryset = super().get_queryset()
        return queryset.filter(author=self.request.user)

    def get_success_url(self):
        # Redirect to the profile page after successful deletion
        messages.success(self.request, "Post deleted successfully!")
        return reverse_lazy('profile')


# Post Like functionality
@login_required
def post_like(request, pk):
    post = get_object_or_404(Post, pk=pk)

    # Check if the user has already liked this post
    existing_like = PostLike.objects.filter(post=post, user=request.user).first()

    if existing_like:
        # If the user already liked the post, remove the like (unlike)
        existing_like.delete()
        messages.success(request, f"You've unliked the post: {post.title}")
    else:
        # If the user hasn't liked the post, create a new like
        PostLike.objects.create(post=post, user=request.user)
        messages.success(request, f"You've liked the post: {post.title}")

    return redirect('post_detail', pk=post.pk)


# Track Post Views
def track_post_view(request, pk):
    post = get_object_or_404(Post, pk=pk)
    
    # Get the user's IP address (or use any other unique identifier if needed)
    user_ip = request.META.get('REMOTE_ADDR')

    # Ensure that a view is logged only once per unique IP per post
    if not PostView.objects.filter(post=post, ip_address=user_ip).exists():
        PostView.objects.create(post=post, ip_address=user_ip)
        post.view_count += 1
        post.save()

    return post


# Post Detail View (with likes and views)
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post = track_post_view(request, pk)  # Track the view for the post

    comments = post.comments.filter(approved=True)  # Fetch approved comments
    new_comment = None
    next_url = request.GET.get('next', '/')

    # Handle form submission for comments
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

    # Fetching the like status of the current user for this post
    user_has_liked = PostLike.objects.filter(post=post, user=request.user).exists()

    return render(request, 'blog/post_detail.html', {
        'post': post,
        'comments': comments,
        'new_comment': new_comment,
        'comment_form': comment_form,
        'next_url': next_url,  # Pass next_url to the template
        'user_has_liked': user_has_liked,  # Pass whether the user has liked the post
    })


def edit_comment(request, id):
    # Fetch the comment object by its ID
    comment = get_object_or_404(Comment, id=id)

    # Ensure the user is the author of the comment
    if comment.author != request.user:
        return HttpResponseForbidden("You are not allowed to edit this comment.")

    # If the request is POST, we process the form
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('post_detail', pk=comment.post.id)
    else:
        form = CommentForm(instance=comment)

    return render(request, 'blog/edit_comment.html', {'form': form, 'comment': comment})


def delete_comment(request, id):
    comment = get_object_or_404(Comment, id=id)

    # Ensure the user is the author of the comment
    if comment.author != request.user:
        return HttpResponseForbidden("You are not allowed to delete this comment.")

    # Delete the comment
    comment.delete()

    return redirect('post_detail', pk=comment.post.id)


