"""Шаблоны URL для приложения blog."""

from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    path('category/<slug:category_slug>/',
         views.CategoryListView.as_view(),
         name='category_posts'),

    path('posts/<int:post_id>/comment/add/',
         views.AddCommentView.as_view(),
         name='add_comment'),
    path('posts/<int:post_id>/comment/edit/<int:pk>/',
         views.EditCommentView.as_view(),
         name='edit_comment'),
    path('posts/<int:post_id>/comment/delete/<int:pk>/',
         views.DeleteCommentView.as_view(),
         name='delete_comment'),
    path('posts/<int:pk>/',
         views.PostDetailView.as_view(),
         name='post_detail'),

    path('posts/create/',
         views.CreatePostView.as_view(),
         name='create_post'),
    path('posts/edit/<int:pk>/',
         views.EditPostView.as_view(),
         name='edit_post'),
    path('posts/delete/<int:pk>/',
         views.DeletePostView.as_view(),
         name='delete_post'),


    # #############################################
    path('accounts/profile/edit/',
         views.EditProfileView.as_view(), name='edit_profile'),
    path('accounts/profile/<str:username>/',
         views.ProfileView.as_view(), name='profile'),

    # # Шаблон URL для страницы по конкретной категории.
    # path(
    #     'category/<slug:category>/',
    #     views.CategoryListView.as_view(),
    #     name='category_posts'
    # ),
    # # Шаблон URL для отдельного поста.
    # path(
    #     'posts/<int:pk>/',
    #     views.PostDetailView.as_view(),
    #     name='post_detail'
    # ),
    # Шаблон URL для главной страницы блога.
    path('', views.PostListView.as_view(), name="index"),
]
