from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.post_list, name='post_list'),
    path('post/<slug:slug>/', views.post_detail, name='post_detail'),
    path('create/', views.create_post, name='create_post'),
    path('add-review/<int:product_id>/', views.add_review, name='add_review'),
]
