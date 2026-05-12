from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='accounts/logout.html', next_page='products:home'), name='logout'),
    path('profile/', views.profile, name='profile'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('wishlist/remove/<int:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('wishlist/add-all-to-cart/', views.add_all_to_cart, name='add_all_to_cart'),
    path('wishlist/clear/', views.clear_wishlist, name='clear_wishlist'),
]
