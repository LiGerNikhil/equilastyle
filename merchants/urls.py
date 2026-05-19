from django.urls import path

from merchants import product_views, views

app_name = 'merchants'

urlpatterns = [
    # Public storefront
    path('store/<slug:slug>/', views.store_home, name='store_home'),
    path('store/<slug:slug>/products/', views.store_products, name='store_products'),
    path('store/<slug:slug>/about/', views.store_about, name='store_about'),
    # Merchant portal
    path('portal/dashboard/', views.merchant_dashboard, name='dashboard'),
    path('portal/orders/', views.merchant_orders, name='orders'),
    path('portal/products/', product_views.merchant_products, name='products'),
    path('portal/products/add/', product_views.merchant_product_create, name='product_add'),
    path('portal/products/<int:product_id>/edit/', product_views.merchant_product_edit, name='product_edit'),
    path('portal/products/<int:product_id>/delete/', product_views.merchant_product_delete, name='product_delete'),
    path('portal/products/size-options/', product_views.merchant_product_size_options, name='product_size_options'),
    path('portal/wallet/', views.merchant_wallet, name='wallet'),
    path('portal/orders/items/<int:item_id>/status/', views.merchant_order_update_status, name='order_item_status'),
]
