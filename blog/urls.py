from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Public pages
    path('', views.PostList.as_view(), name='home'),  # Home page (List of posts)
    path('about/', views.AboutPage.as_view(), name='about'),  # About page

    # Post-related views
    path('post/<int:pk>/', views.PostDetailView.as_view(), name='post_detail'),  # View post details
    path('post/new/', views.PostCreateView.as_view(), name='post-create'),  # Create a new post
    path('post/<int:pk>/edit/', views.PostUpdateView.as_view(), name='post-edit'),  # Edit a post
    path('post/<int:pk>/delete/', views.PostDeleteView.as_view(), name='post-delete'),  # Delete a post

    # Authentication views
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),  # Login page
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),  # Logout and redirect to home
    path('register/', views.register, name='register'),  # User registration
    path('profile/', views.profile, name='profile'),  # User profile page
]
