from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Public pages
    path('', views.PostList.as_view(), name='home'),
    path('about/', views.AboutPage.as_view(), name='about'),

    # Post-related views
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
    path('post/<int:pk>/like/', views.post_like, name='post_like'),
    # path('post/<int:pk>/', views.post_detail, name='post_detail'),
    path('post/new/', views.PostCreateView.as_view(), name='post-create'),
    path('post/<int:pk>/edit/', views.PostUpdateView.as_view(), name='post-edit'),
    path('post/<int:pk>/delete/', views.PostDeleteView.as_view(), name='post-delete'),
    path('comment/<int:id>/edit/', views.edit_comment, name='comment-edit'),
    path('comment/<int:id>/delete/', views.delete_comment, name='comment-delete'),

    # Authentication views
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
]
