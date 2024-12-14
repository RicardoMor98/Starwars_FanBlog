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
from .models import Post
from .forms import UserRegisterForm

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
    # Fetch only posts created by the logged-in user
    user_posts = Post.objects.filter(author=request.user)
    context = {
        'posts': user_posts,
        'post_count': user_posts.count(),  # Total number of posts
        'user': request.user,  # Logged-in user's details
    }

    # Render the profile page with additional data
    return render(request, 'blog/profile.html', context)

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'content', 'status']  # Include fields you want in the form
    template_name = 'blog/post_form.html'  # Template for creating posts

    def form_valid(self, form):
        # Automatically assign the logged-in user as the author
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        # Redirect to the profile page after a successful post creation
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