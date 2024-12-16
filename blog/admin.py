from django.contrib import admin
from .models import Post, Comment
from django_summernote.admin import SummernoteModelAdmin

# Register the Post model with custom admin configuration
@admin.register(Post)
class PostAdmin(SummernoteModelAdmin):
    list_display = ('title', 'slug', 'status', 'created_on')
    search_fields = ['title', 'content']
    list_filter = ('status', 'created_on',)
    prepopulated_fields = {'slug': ('title',)}
    summernote_fields = ('content',)

# Register the Comment model with custom admin configuration
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'post', 'body', 'created_on', 'approved')
    list_filter = ('approved', 'created_on')
    search_fields = ('author__username', 'body', 'post__title')
    actions = ['approve_comments']

    def approve_comments(self, request, queryset):
        # Set the `approved` field of selected comments to True
        queryset.update(approved=True)
    approve_comments.short_description = "Approve selected comments"  # Optional: Set a short description for the action

# Register CommentAdmin with the Comment model
admin.site.register(Comment, CommentAdmin)
