from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    path('dashboard/', views.admin_dashboard, name='dashboard'),
    path('users/', views.admin_users, name='users'),
    path('users/<int:user_id>/edit/', views.admin_user_edit, name='user_edit'),
    path('users/<int:user_id>/toggle-status/', views.admin_user_toggle_status, name='user_toggle_status'),
    path('users/<int:user_id>/delete/', views.admin_user_delete, name='user_delete'),
    path('products/', views.admin_products, name='products'),
    path('products/add/', views.admin_product_create, name='product_add'),
    path('products/<int:product_id>/edit/', views.admin_product_edit, name='product_edit'),
    path('products/size-options/', views.admin_product_size_options, name='product_size_options'),
    path('products/<int:product_id>/toggle-status/', views.admin_product_toggle_status, name='product_toggle_status'),
    path('products/<int:product_id>/delete/', views.admin_product_delete, name='product_delete'),
    path('products/approvals/', views.admin_product_approvals, name='product_approvals'),
    path('products/<int:product_id>/review/', views.admin_product_review, name='product_review'),
    path('products/<int:product_id>/approve/', views.admin_product_approve, name='product_approve'),
    path('merchants/', views.admin_merchants, name='merchants'),
    path('merchants/add/', views.admin_merchant_create, name='merchant_add'),
    path('merchants/<int:merchant_id>/edit/', views.admin_merchant_edit, name='merchant_edit'),
    path('merchants/<int:merchant_id>/toggle-status/', views.admin_merchant_toggle_status, name='merchant_toggle_status'),
    path('merchants/<int:merchant_id>/verify/', views.admin_merchant_verify, name='merchant_verify'),
    path('merchants/<int:merchant_id>/delete/', views.admin_merchant_delete, name='merchant_delete'),
    path('orders/', views.admin_orders, name='orders'),
    path('orders/<int:order_id>/', views.admin_order_detail, name='order_detail'),
    path('orders/<int:order_id>/update-status/', views.admin_order_update_status, name='order_update_status'),
    path('blog/', views.admin_blog, name='blog'),
    path('blog/<int:post_id>/edit/', views.admin_blog_edit, name='blog_edit'),
    path('blog/<int:post_id>/toggle-status/', views.admin_blog_toggle_status, name='blog_toggle_status'),
    path('blog/<int:post_id>/delete/', views.admin_blog_delete, name='blog_delete'),
    # Notification API endpoints
    path('api/notifications/', views.notification_api, name='notification_api'),
    path('api/notifications/<int:notification_id>/mark-read/', views.mark_notification_read, name='mark_notification_read'),
    path('api/notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('api/notifications/stream/', views.notification_stream, name='notification_stream'),
]
