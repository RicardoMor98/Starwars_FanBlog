from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.PostList.as_view(), name='home'),  # Home page (List of posts)
    path('about/', views.AboutPage.as_view(), name='about'),  # About page
    path('post/new/', views.PostCreateView.as_view(), name='post-create'),  # Create a new post
    path('post/<int:pk>/edit/', views.PostUpdateView.as_view(), name='post-edit'),  # Edit post
    path('post/<int:pk>/delete/', views.PostDeleteView.as_view(), name='post-delete'),  # Delete post
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),  # Login
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),  # Logout
    path('register/', views.register, name='register'),  # User registration
    path('profile/', views.profile, name='profile'),  # User profile page
]
