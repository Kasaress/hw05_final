from django.urls import path

from . import views
from .views import PostDeleteView

app_name = 'posts'

urlpatterns = [
    path('profile/<str:username>/unfollow/',
         views.profile_unfollow,
         name='profile_unfollow'),
    path('profile/<str:username>/follow/',
         views.profile_follow,
         name='profile_follow'),
    path('follow/', views.follow_index, name='follow_index'),
    path('posts/<int:post_id>/comment/',
         views.add_comment, name='add_comment'),
    path('posts/<int:post_id>/delete/',
         PostDeleteView.as_view(), name='post_delete'),
    path('create/', views.post_create, name='post_create'),
    path('posts/<int:post_id>/edit/', views.post_edit, name='post_edit'),
    path('posts/<int:post_id>/', views.post_detail, name='post_detail'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('group/<slug:slug>/', views.group_posts, name='group_list'),
    path('', views.index, name='index'),
]
