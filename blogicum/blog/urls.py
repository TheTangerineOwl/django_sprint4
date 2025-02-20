"""Шаблоны URL для приложения blog."""

from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    path('category/<slug:category_slug>/',
         views.CategoryListView.as_view(),
         name='category_posts'),

    path('posts/<int:post_id>/add_comment/',
         views.AddCommentView.as_view(),
         name='add_comment'),
    path('posts/<int:post_id>/edit_comment/<int:comment_id>/',
         views.EditCommentView.as_view(),
         name='edit_comment'),
    path('posts/<int:post_id>/delete_comment/<int:comment_id>/',
         views.DeleteCommentView.as_view(),
         name='delete_comment'),
    # path('posts/<int:post_id>/edit_comment/<int:comment_id>/',
    #      views.edit_comment, name='edit_comment'),
    # path('posts/<int:post_id>/delete_comment/<int:comment_id>/',
    #      views.delete_comment, name='delete_comment'),


    path('posts/<int:post_id>/',
         views.PostDetailView.as_view(),
         name='post_detail'),

    path('posts/create/',
         views.CreatePostView.as_view(),
         name='create_post'),
    path('posts/<int:post_id>/edit/',
         views.EditPostView.as_view(),
         name='edit_post'),
    path('posts/<int:post_id>/delete/',
         views.DeletePostView.as_view(),
         name='delete_post'),


    # #############################################
    path('profile/edit/',
         views.EditProfileView.as_view(), name='edit_profile'),
    path('profile/<str:username>/',
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
