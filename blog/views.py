from django.shortcuts import render, redirect
from django.views import generic
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView
from django.views.generic.edit import UpdateView
from django.views.generic.edit import DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from .models import Post, Comment
from .forms import UserRegisterForm
from django.views.generic import DetailView
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, get_object_or_404, redirect
from .forms import CommentForm


# Home page view to display published posts
class PostList(generic.ListView):
    queryset = Post.objects.filter(status=1)  # Only published posts (status=1)
    template_name = "blog/index.html"  # Template for the home page
    paginate_by = 6  # Pagination: 6 posts per page

# About page view
class AboutPage(TemplateView):
    template_name = 'blog/about.html'  # Template for the about page

# User registration view
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()  # Save the new user
            username = form.cleaned_data.get('username')  # Get the username
            # Success message to inform the user their account was created
            messages.success(request, f'Account created for {username}! You can now log in.')
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
    template_name = 'blog/post_form.html'  # Template for the post creation form

    def form_valid(self, form):
        """Override form_valid to assign the current user as the post author."""
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        """Redirect to the profile page upon successful creation."""
        return reverse_lazy('profile')


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    fields = ['title', 'content', 'status']  # Fields to display in the form
    template_name = 'blog/post_form.html'  # Reuse the form template for creating and updating posts

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
    template_name = 'blog/post_confirm_delete.html'  # Template for confirming deletion

    def get_queryset(self):
        # Ensure the user can only delete their own posts
        queryset = super().get_queryset()
        return queryset.filter(author=self.request.user)

    def get_success_url(self):
        # Redirect to the profile page after successful deletion
        messages.success(self.request, "Post deleted successfully!")
        return reverse_lazy('profile')

def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    comments = post.comments.filter(approved=True)  # Fetch approved comments
    new_comment = None
    next_url = request.GET.get('next', '/')  # Retrieve the 'next' URL parameter

    # Handle form submission for comments
    if request.method == "POST":
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.author = request.user  # Set the current user as the author
            new_comment.save()
            messages.success(request, "Your comment has been submitted for review.")
            return redirect("post_detail", pk=post.pk)  # Redirect to the same post page
    else:
        comment_form = CommentForm()

    return render(request, 'blog/post_detail.html', {
        'post': post,
        'comments': comments,
        'new_comment': new_comment,
        'comment_form': comment_form,
        'next_url': next_url,  # Pass next_url to the template
    })

#class PostDetailView(DetailView):
#    model = Post
#    template_name = 'blog/post_detail.html'
#    context_object_name = 'post'

#def login_view(request):
#    if request.method == "POST":
#        form = AuthenticationForm(data=request.POST)
#        if form.is_valid():
#            user = form.get_user()
#            login(request, user)
#            # Redirect to the profile page after login
#            return redirect('profile')  # 'profile' should be the name of your profile URL
#    else:
#        form = AuthenticationForm()
#
#    return render(request, 'login.html', {'form': form})

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
            return redirect('post_detail', pk=comment.post.id)  # Redirect to the post detail page
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

    return redirect('post_detail', pk=comment.post.id)  # Redirect to the post detail page

    