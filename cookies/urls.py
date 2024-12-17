from django.urls import path
from .views import *
from django.views.decorators.cache import cache_page

urlpatterns = [
    path('', cache_page(60*15)(IndexView.as_view()), name='home'),
    path('category/<int:pk>/', CategoryListView.as_view(), name='category_list'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='post_detail'),
    path('add-post/', PostCreateView.as_view(), name='add_post'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('post/<int:pk>/update/', PostUpdateView.as_view(), name='post_update'),
    path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='post_delete'),
    path('search/', SearchView.as_view(), name='search'),

    path('add_comment/<int:post_id>/', add_comment, name='add_comment'),
    path('comments/<int:comment_id>/like/', like_comment, name='like_comment'),
    path('comments/<int:comment_id>/dislike/', dislike_comment, name='dislike_comment'),
    path('register/', register, name='register'),
    path('profile/<str:identifier>/', profile_view, name='profile'),
    path('profile/<str:username>/edit/', edit_profile, name='edit_profile'),

    # Добавьте другие пути по необходимости
]