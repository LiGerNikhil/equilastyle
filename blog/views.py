from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils.text import slugify
from .models import Post, Category
from .forms import PostCreateForm
from products.models import Product, Review


def post_list(request):
    posts = Post.objects.filter(status='published')
    categories = Category.objects.all()
    featured_posts = posts.filter(is_featured=True)[:3]
    
    category_slug = request.GET.get('category')
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        posts = posts.filter(category=category)
    
    context = {
        'posts': posts,
        'categories': categories,
        'featured_posts': featured_posts,
    }
    return render(request, 'blog/post_list.html', context)


def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug, status='published')
    post.views += 1
    post.save()
    
    related_posts = Post.objects.filter(
        category=post.category,
        status='published'
    ).exclude(id=post.id)[:3]
    
    context = {
        'post': post,
        'related_posts': related_posts,
    }
    return render(request, 'blog/post_detail.html', context)


@login_required
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        rating = request.POST.get('rating')
        title = request.POST.get('title')
        content = request.POST.get('content')
        
        if rating and title and content:
            # Check if user already reviewed this product
            existing_review = Review.objects.filter(product=product, user=request.user).first()
            if existing_review:
                # Update existing review
                existing_review.rating = int(rating)
                existing_review.title = title
                existing_review.content = content
                existing_review.save()
                messages.success(request, 'Your review has been updated successfully!')
            else:
                # Create new review
                Review.objects.create(
                    product=product,
                    user=request.user,
                    rating=int(rating),
                    title=title,
                    content=content,
                    is_verified_purchase=True  # Assuming user has purchased
                )
                messages.success(request, 'Your review has been submitted successfully!')
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Review submitted successfully!',
                    'rating': rating,
                    'title': title,
                    'content': content
                })
            else:
                return redirect('products:product_detail', slug=product.slug)
        else:
            messages.error(request, 'Please fill in all fields.')
    
    return redirect('products:product_detail', slug=product.slug)


@login_required
def create_post(request):
    """Allow authenticated users to create blog posts"""
    if request.method == 'POST':
        form = PostCreateForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.slug = slugify(post.title)
            post.status = 'published'  # Publish immediately
            post.save()
            messages.success(request, 'Your post has been published successfully!')
            return redirect('blog:post_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PostCreateForm()
    
    return render(request, 'blog/create_post.html', {'form': form})
