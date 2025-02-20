"""CBV-представления для приложения blog."""

from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordResetView
# from django.contrib.auth.forms import UserCreationForm
from django.views.generic import (DetailView, ListView, CreateView,
                                  DeleteView, UpdateView)
from django.utils import timezone
from django.db.models import Count
from django.http import Http404
from django.urls import reverse_lazy, reverse
from django.core.mail import send_mail

from .models import Category, Post, Comment, User
from .forms import CommentForm, PostForm, UserForm, UserRegistrationForm


PAGES = 10


class PostMixin:
    def get_queryset(self):
        return Post.objects.select_related(
            'category',
            'location',
            'author'
        ).annotate(comment_count=Count('comments')).filter(
            is_published=True,
            pub_date__lte=timezone.now()
        ).order_by('-pub_date')


class PostListView(PostMixin, ListView):

    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'    
    paginate_by = PAGES

    def get_queryset(self):
        return super().get_queryset().filter(category__is_published=True)

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     # context['post_count'] = self.get_queryset().count()
    #     # if context['object_list']:
    #         # print(context['object_list'])
    #     # con = {'':0}
    #     #context.pop('object_list')
    #     # if context['object_list']:
    #     #     print(context['object_list'])
    #     print(context['post_list'])
    #     print(context['page_obj'])
    #     print(context['paginator'])
    #     # print(context['page_obj'].has_other_pages)
    #     # context['page_obj'] = context['object_list']
    #     # context['page_obj'] = self.get_queryset()
    #     # context['post_count'] = self.get_queryset().count()
    #     return context


# class PostDetailView(DetailView):
#     model = Post
#     post = None
#     template_name = 'blog/detail.html'
#     context_object_name = 'post'

#     def get_object(self):
#         # post = super().get_object()
#         # post = super().get_object()
#         post = get_object_or_404(
#             Post,
#             pk=self.kwargs['post_id']
#         )
#         if not post.is_published and self.request.user != post.author:
#             raise Http404("Post not found")
#         return post

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['form'] = CommentForm()
#         # context['post'] = self.post
#         context['comments'
#                 ] = Comment.objects.select_related('author'
#                                                    ).filter(post=self.object)
#         return context

#     def dispatch(self, request, *args, **kwargs):
#         self.post = get_object_or_404(
#             Post,
#             pk=kwargs['post_id'],
#             is_published=True,
#             category__is_published=True,
#             pub_date__lte=timezone.now()
#         )
#         return super().dispatch(request, *args, **kwargs)


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'
    pk_url_kwarg = 'post_id'

    def get_object(self):
        post = super().get_object()
        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'
                ] = Comment.objects.select_related('author'
                                                   ).filter(post=self.object)
        return context

    def dispatch(self, request, *args, **kwargs):
        post = get_object_or_404(
            Post,
            pk=kwargs['post_id']
        )
        if (request.user != post.author):
            if not (post.category.is_published and post.is_published
                    and post.pub_date <= timezone.now()):
                raise Http404("Пост не найден")

        # post = get_object_or_404(
        #     Post,
        #     pk=kwargs['post_id'],
        #     pub_date__lte=timezone.now()
        # )
        
        # # Проверяем, опубликован ли пост или является ли пользователь автором
        # if not post.is_published and request.user != post.author:
        #     # Проверяем, опубликована ли категория
        #     # if not post.category.is_published:
        #     raise Http404("Post not found")
        
        return super().dispatch(request, *args, **kwargs)


class CategoryListView(PostMixin, ListView):
    # category = None
    model = Post
    template_name = 'blog/category.html'
    context_object_name = 'post_list'
    # context_object_name = 'post_list'
    paginate_by = PAGES
    ordering = '-pub_date'

    def get_queryset(self):
        category = get_object_or_404(Category,
                                     slug=self.kwargs['category_slug'],
                                     is_published=True)
        return super().get_queryset().filter(category=category)

    def dispatch(self, request, *args, **kwargs):
        query_set = Category.objects.filter(
            slug=kwargs['category_slug'],
            is_published=True
        )
        self.category = get_object_or_404(query_set)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class CreatePostView(LoginRequiredMixin, CreateView):
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blog:profile', args=[self.request.user.username])

    def dispatch(self, request, *args, **kwargs):
        # Проверяем, авторизован ли пользователь
        if not request.user.is_authenticated:
            # Если не авторизован, перенаправляем
            return redirect(reverse('blog:index'))
        return super().dispatch(request, *args, **kwargs)


# class EditPostView(LoginRequiredMixin, UpdateView):
#     model = Post
#     form_class = PostForm
#     template_name = 'blog/create.html'

#     def get_object(self):
#         # post = super().get_object()
#         post = get_object_or_404(
#             Post,
#             pk=self.kwargs['post_id']
#         )
#         if post.author != self.request.user:
#             raise Http404("You are not allowed to edit this post.")
#         return post

#     def get_success_url(self):
#         return reverse_lazy('blog:post_detail', args=[self.object.id])

#     def dispatch(self, request, *args, **kwargs):
#         # Проверяем, авторизован ли пользователь
#         if not request.user.is_authenticated:
#             # Если не авторизован, перенаправляем
#             # return reverse_lazy('blog:post_detail', args=[self.object.id])
#             return redirect(reverse_lazy('blog:post_detail',
#                             args=[kwargs['post_id']]))
#         return super().dispatch(request, *args, **kwargs)
    
#     def form_valid(self, form):
#         form.instance.author = self.request.user
#         # #############################################
#         # self.request.user.is_authenticated = True
#         if not self.request.user.is_authenticated:
#             # Если не авторизован, перенаправляем
#             # return reverse_lazy('blog:post_detail', args=[self.object.id])
#             return redirect(reverse_lazy('blog:post_detail',
#                             args=[self.kwargs['post_id']]))
#         return super().form_valid(form)


# class EditPostView(UpdateView):
#     model = Post
#     form_class = PostForm
#     template_name = 'blog/create.html'

#     def get_object(self):
#         post = get_object_or_404(Post, pk=self.kwargs['post_id'])
#         if post.author != self.request.user:
#             # raise Http404("You are not allowed to edit this post.")
#             return redirect(reverse_lazy('blog:post_detail', args=[post.id]))
#         return post

#     def get_success_url(self):
#         return reverse_lazy('blog:post_detail', args=[self.object.id])


class EditPostView(UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'  # Указываем, что используем 'post_id' как параметр для pk

    def dispatch(self, request, *args, **kwargs):
        post = get_object_or_404(Post, pk=kwargs[self.pk_url_kwarg])
        if post.author != request.user:
            return redirect(reverse_lazy('blog:post_detail', args=[post.id]))
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('blog:post_detail', args=[self.object.id])


    # def dispatch(self, request, *args, **kwargs):
    #     # Проверяем, авторизован ли пользователь
    #     if not request.user.is_authenticated:
    #         # Если не авторизован, перенаправляем на страницу публикации
    #         return redirect(reverse_lazy('blog:post_detail',
    #                                      args=[kwargs['post_id']]))
    #     return super().dispatch(request, *args, **kwargs)

    # def form_valid(self, form):
    #     if not self.request.user.is_authenticated:
    #         # Если не авторизован, перенаправляем на страницу публикации
    #         return redirect(reverse_lazy('blog:post_detail',
    #                                      args=[self.kwargs['post_id']]))
    #     return super().form_valid(form)


# class DeletePostView(DeleteView):
#     model = Post
#     template_name = 'blog/create.html'

#     def get_object(self):
#         # post = super().get_object()
#         post = get_object_or_404(
#             Post,
#             pk=self.kwargs['post_id']
#         )
#         if post.author != self.request.user:
#             # raise Http404("You are not allowed to delete this post.")
#             return redirect(reverse_lazy('blog:post_detail', args=[post.id]))
#         return post

#     def get_context_data(self, **kwargs):
#         # Получаем контекст от родительского класса
#         context = super().get_context_data(**kwargs)
#         # Удаляем форму из контекста
#         if 'form' in context:
#             del context['form']
#         return context

#     def get_success_url(self):
#         return reverse_lazy('blog:index')


class DeletePostView(DeleteView):
    model = Post
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        post = get_object_or_404(Post, pk=kwargs[self.pk_url_kwarg])
        if post.author != request.user:
            return redirect(reverse_lazy('blog:post_detail', args=[post.id]))
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('blog:index')
    
    def get_context_data(self, **kwargs):
        # Получаем контекст от родительского класса
        context = super().get_context_data(**kwargs)
        # Удаляем форму из контекста
        if 'form' in context:
            del context['form']
        return context


    # def dispatch(self, request, *args, **kwargs):
    #     # Проверяем, авторизован ли пользователь
    #     if not request.user.is_authenticated:
    #         # Если не авторизован, перенаправляем
    #         return reverse_lazy('blog:post_detail', args=[self.object.id])
    #     return super().dispatch(request, *args, **kwargs)


class AddCommentView(LoginRequiredMixin, CreateView):
    form_class = CommentForm
    template_name = 'blog/comment.html'
    # paginate_by = PAGES

    def form_valid(self, form):
        post = get_object_or_404(Post, id=self.kwargs['post_id'])
        form.instance.author = self.request.user
        form.instance.post = post
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blog:post_detail', args=[self.kwargs['post_id']])

    def dispatch(self, request, *args, **kwargs):
        # Проверяем, авторизован ли пользователь
        if not request.user.is_authenticated:
            # Если не авторизован, перенаправляем
            return redirect(reverse('login'))
        return super().dispatch(request, *args, **kwargs)


# class EditCommentView(UpdateView):
#     model = Comment
#     form_class = CommentForm
#     template_name = 'blog/comment.html'

#     def get_object(self):
#         comment = super().get_object(Comment.objects.get(pk=self.kwargs['comment_id']))
#         if comment.author != self.request.user:
#             raise Http404("You are not allowed to edit this comment.")
#         return comment

#     def get_success_url(self):
#         return reverse_lazy('blog:post_detail', args=[self.object.post.id])

#     def dispatch(self, request, *args, **kwargs):
#         # Проверяем, авторизован ли пользователь
#         if not request.user.is_authenticated:
#             # Если не авторизован, перенаправляем
#             return redirect(reverse_lazy('blog:post_detail',
#                                          args=[kwargs['pk']]))
#         return super().dispatch(request, *args, **kwargs)


# class DeleteCommentView(DeleteView):
#     model = Comment
#     # form_class = CommentForm
#     template_name = 'blog/comment_delete.html'

#     def get_object(self):
#         comment = super().get_object()
#         if comment.author != self.request.user:
#             raise Http404("You are not allowed to delete this comment.")
#         return comment

#     def get_success_url(self):
#         return reverse_lazy('blog:post_detail', args=[self.object.post.id])

#     def dispatch(self, request, *args, **kwargs):
#         # Проверяем, авторизован ли пользователь
#         if not request.user.is_authenticated:
#             # Если не авторизован, перенаправляем
#             return redirect(reverse_lazy('blog:post_detail',
#                                          args=[kwargs['post_id']]))
#         return super().dispatch(request, *args, **kwargs)


class EditCommentView(UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def get_object(self):
        comment = get_object_or_404(Comment,
                                    id=self.kwargs['comment_id'],
                                    post_id=self.kwargs['post_id'])
        if comment.author != self.request.user:
            raise Http404("You are not allowed to edit this comment.")
        return comment

    def get_success_url(self):
        return reverse_lazy('blog:post_detail', args=[self.object.post.id])

    # def dispatch(self, request, *args, **kwargs):
    #     # Проверяем, авторизован ли пользователь
    #     if not request.user.is_authenticated:
    #         # Если не авторизован, перенаправляем
    #         return redirect(reverse_lazy('blog:post_detail',
    #                                      args=[kwargs['post_id']]))
    #     return super().dispatch(request, *args, **kwargs)


class DeleteCommentView(DeleteView):
    model = Comment
    # form_class = CommentForm
    template_name = 'blog/comment.html'

    def get_object(self):
        comment = get_object_or_404(Comment,
                                    id=self.kwargs['comment_id'],
                                    post_id=self.kwargs['post_id'])
        if comment.author != self.request.user:
            raise Http404("You are not allowed to edit this comment.")
        return comment

    def get_context_data(self, **kwargs):
        # Получаем контекст от родительского класса
        context = super().get_context_data(**kwargs)
        # Удаляем форму из контекста
        if 'form' in context:
            del context['form']
        return context

    def get_success_url(self):
        return reverse_lazy('blog:post_detail', args=[self.object.post.id])


# from django.shortcuts import render
# from django.contrib.auth.decorators import login_required
# @login_required
# def edit_comment(request, post_id, comment_id):
#     comment = get_object_or_404(Comment, id=comment_id, post_id=post_id)

#     # Проверка, является ли текущий пользователь автором комментария
#     if comment.author != request.user:
#         raise Http404("You are not allowed to edit this comment.")

#     if request.method == 'POST':
#         form = CommentForm(request.POST, instance=comment)
#         if form.is_valid():
#             form.save()
#             return redirect(reverse_lazy('blog:post_detail', args=[comment.post.id]))
#     else:
#         form = CommentForm(instance=comment)

#     return render(request, 'blog/comment.html', {'form': form, 'comment': comment})


# @login_required
# def delete_comment(request, post_id, comment_id):
#     comment = get_object_or_404(Comment, id=comment_id, post_id=post_id)

#     # Проверка, является ли текущий пользователь автором комментария
#     if comment.author != request.user:
#         raise Http404("You are not allowed to delete this comment.")

#     if request.method == 'POST':
#         comment.delete()
#         return redirect(reverse_lazy('blog:post_detail', args=[comment.post.id]))

#     return render(request, 'blog/comment_delete.html', {'object': comment})


class ProfileView(PostMixin, ListView):

    paginate_by = PAGES
    model = Post

    template_name = 'blog/profile.html'
    context_object_name = 'post_list'

    def get_queryset(self):
        profile = get_object_or_404(User, username=self.kwargs['username'])
        if self.request.user != profile:
            return super().get_queryset().filter(author=profile,
                                                 category__is_published=True)
        # return Post.objects.filter(author=profile)
        return Post.objects.select_related(
            'category',
            'location',
            'author'
        ).annotate(comment_count=Count('comments')).filter(
            author=profile
        ).order_by('-pub_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'
                ] = get_object_or_404(User, username=self.kwargs['username'])
        return context


class EditProfileView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserForm
    template_name = 'blog/user.html'

    def get_object(self):

        # if self.kwargs['profile'] != self.request.user:
            # raise Http404("You are not allowed to edit this.")
        return get_object_or_404(User, username=self.request.user.username)

    def get_success_url(self):
        return reverse_lazy('blog:profile', args=[self.request.user.username])

    def dispatch(self, request, *args, **kwargs):
        # Проверяем, авторизован ли пользователь
        # if not request.user.is_authenticated:
            # Если не авторизован, перенаправляем
            # return reverse_lazy('login')
        return super().dispatch(request, *args, **kwargs)


class RegistrationView(CreateView):
    template_name = 'registration/registration_form.html'
    # form_class = UserCreationForm
    form_class = UserRegistrationForm
    success_url = reverse_lazy('blog:index')

    def form_valid(self, form):
        response = super().form_valid(form)

        send_mail(
            'Добро пожаловать!',
            'Спасибо за регистрацию на нашем сайте.',
            'from@example.com',
            [form.cleaned_data['email']],
        )

        return response


class PasswordResetEmailView(PasswordResetView):

    def form_valid(self, form):  # , **kwargs):
        response = super().form_valid(form)
        # context = self.get_context_data(form=form, **kwargs)

        email = form.cleaned_data.get('email')
        if email:
            send_mail(
                subject='Сброс пароля',
                message='Пользователь запросил сброс пароля. ' +
                'Если это были не вы, обратитесь к администратору.',
                from_email='admin@example.com',
                recipient_list=[email, ],
            )
        else:
            response = super().form_invalid()

        return response
