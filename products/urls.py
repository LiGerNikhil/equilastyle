from django.urls import path
from . import views
from . import api_views
from . import wishlist_views

app_name = 'products'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('privacy/', views.privacy, name='privacy'),
    path('terms/', views.terms, name='terms'),
    path('cookies/', views.cookies, name='cookies'),
    path('shipping/', views.shipping, name='shipping'),
    path('returns/', views.returns, name='returns'),
    path('size-guide/', views.size_guide, name='size_guide'),
    path('products/', views.product_list, name='product_list'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('category/<slug:slug>/', views.category_products, name='category_products'),
    path('brand/<slug:slug>/', views.brand_products, name='brand_products'),
    path('search/', views.search_products, name='search_products'),

    path('api/products/', api_views.products_api, name='products_api'),
    path('api/products/<int:product_id>/', api_views.product_api, name='product_api'),
    path('api/public/products/<int:product_id>/', api_views.public_product_detail, name='public_product_detail'),
    
    # Wishlist URLs
    path('wishlist/add/<int:product_id>/', wishlist_views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:product_id>/', wishlist_views.remove_from_wishlist, name='remove_from_wishlist'),
    path('wishlist/toggle/<int:product_id>/', wishlist_views.toggle_wishlist, name='toggle_wishlist'),
    path('wishlist/', wishlist_views.get_wishlist, name='get_wishlist'),
]
