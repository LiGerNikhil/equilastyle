from django.contrib import admin
from .models import Category, Post, Comment


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'status', 'is_featured', 'created_at']
    list_filter = ['status', 'is_featured', 'category', 'created_at']
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ['author']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('author', 'category')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['post', 'author', 'is_approved', 'created_at']
    list_filter = ['is_approved', 'created_at']
    search_fields = ['post__title', 'author__email', 'content']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('post', 'author')
