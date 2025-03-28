from django.db import models
from django.contrib.auth.models import User

STATUS = ((0, "Draft"), (1, "Published"))

# Create your models here.
class Post(models.Model):
    title = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="blog_posts"
    )
    content = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    status = models.IntegerField(choices=STATUS, default=0)
    excerpt = models.TextField(blank=True)
    image = models.ImageField(upload_to='post_images/', blank=True, null=True)

    # Additional fields for like, dislike, and view counts
    like_count = models.IntegerField(default=0)
    dislike_count = models.IntegerField(default=0)
    view_count = models.IntegerField(default=0)

    class Meta:
        ordering = ["-created_on"]
        verbose_name = "Blog Post"
        verbose_name_plural = "Blog Posts"

    def __str__(self):
        return f"{self.title} | written by {self.author}"

    def increment_view_count(self):
        """Method to increment the view count"""
        self.view_count += 1
        self.save()

    def increment_like(self):
        """Method to increment the like count"""
        self.like_count += 1
        self.save()

    def increment_dislike(self):
        """Method to increment the dislike count"""
        self.dislike_count += 1
        self.save()


class Comment(models.Model):
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="comments_author")
    body = models.TextField()
    approved = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_on"]
        verbose_name = "Comment"
        verbose_name_plural = "Comments"

    def __str__(self):
        return f"Comment by {self.author} on {self.post.title}"

class PostLike(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="likes")
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'user')  # Ensure a user can only like/dislike once per post

    def __str__(self):
        return f"Like by {self.user} on {self.post.title}"

class PostView(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="views")
    ip_address = models.GenericIPAddressField()
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"View by {self.ip_address} on {self.post.title}"
