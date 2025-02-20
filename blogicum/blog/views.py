"""CBV-представления для приложения blog."""

from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordResetView
from django.views.generic import (DetailView, ListView, CreateView,
                                  DeleteView, UpdateView)
from django.utils import timezone
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.db.models import Count
from django.http import Http404
from django.urls import reverse_lazy, reverse
from django.core.mail import send_mail
from random import choice
from string import ascii_letters, punctuation, digits
from django.template.loader import render_to_string
from django.contrib.auth.tokens import PasswordResetTokenGenerator

from .models import Category, Post, Comment, User
from .forms import CommentForm, PostForm, UserForm, UserRegistrationForm


# Количество постов на одной странице пагинатора.
PAGES = 10


class PostMixin:
    """Миксин для страниц, взаимодействующих с постами."""

    def get_queryset(self):
        """Получение набора общедоступных постов."""
        return Post.objects.select_related(
            'category',
            'location',
            'author'
        ).annotate(comment_count=Count('comments')).filter(
            category__is_published=True,
            is_published=True,
            pub_date__lte=timezone.now()
        ).order_by('-pub_date')


class PostListView(PostMixin, ListView):
    """Главная страница блога."""

    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'
    paginate_by = PAGES

    def get_queryset(self):
        """Получение набора общедоступных постов."""
        return super().get_queryset().filter(category__is_published=True)


class PostDetailView(DetailView):
    """Страница отдельного поста."""

    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'
    pk_url_kwarg = 'post_id'

    def get_object(self):
        """Получения поста с заданным post_id"""
        post = super().get_object()
        return post

    def get_context_data(self, **kwargs):
        """Получение формы и комментариев к посту в контексте."""
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'
                ] = Comment.objects.select_related('author'
                                                   ).filter(post=self.object)
        return context

    def dispatch(self, request, *args, **kwargs):
        """Обработка доступности поста, иначе возвращает ошибку."""
        post = get_object_or_404(
            Post,
            pk=kwargs['post_id']
        )
        # Автор может просматривать все свои существующие посты.
        if (request.user != post.author):
            # Не автор может просматривать только уже опубликованные.
            if not (post.category.is_published and post.is_published
                    and post.pub_date <= timezone.now()):
                raise Http404("Пост не найден")

        return super().dispatch(request, *args, **kwargs)


class CategoryListView(PostMixin, ListView):
    """Страница постов в данной категории."""

    model = Post
    template_name = 'blog/category.html'
    context_object_name = 'post_list'
    paginate_by = PAGES
    ordering = '-pub_date'

    def get_queryset(self):
        """Получение постов в заданной категории или ошибки 404."""
        category = get_object_or_404(Category,
                                     slug=self.kwargs['category_slug'],
                                     is_published=True)
        return super().get_queryset().filter(category=category)

    def dispatch(self, request, *args, **kwargs):
        """Получение опубликованных постов в категории."""
        query_set = Category.objects.filter(
            slug=kwargs['category_slug'],
            is_published=True
        )
        self.category = get_object_or_404(query_set)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Передача категории в контекст страницы."""
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class CreatePostView(LoginRequiredMixin, CreateView):
    """Страница создания нового поста."""

    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        """При корректности заполнения формы задает автора и сохраняет ее."""
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        """Перенаправляет при успешном создании поста."""
        return reverse_lazy('blog:profile', args=[self.request.user.username])

    def dispatch(self, request, *args, **kwargs):
        """Перенаправление для неавторизованных пользователей."""
        if not request.user.is_authenticated:
            return redirect(reverse('blog:index'))
        return super().dispatch(request, *args, **kwargs)


class EditPostView(UpdateView):
    """Страница редактирования поста."""

    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    # Указываем, что используем 'post_id' как параметр для pk
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        """Если пользователь не автор, перенаправляет на страницу поста."""
        post = get_object_or_404(Post, pk=kwargs[self.pk_url_kwarg])
        if post.author != request.user:
            return redirect(reverse_lazy('blog:post_detail', args=[post.id]))
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        """Перенаправление при успешном изменении."""
        return reverse_lazy('blog:post_detail', args=[self.object.id])


class DeletePostView(DeleteView):
    """Страница удаления поста."""

    model = Post
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        """Если пользователь не автор, перенаправляет на страницу поста."""
        post = get_object_or_404(Post, pk=kwargs[self.pk_url_kwarg])
        if post.author != request.user:
            return redirect(reverse_lazy('blog:post_detail', args=[post.id]))
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        """Перенаправление на главную страницу при успешном удалении."""
        return reverse_lazy('blog:index')

    def get_context_data(self, **kwargs):
        """Удаление формы из контекста класа и передача на страницу"""
        context = super().get_context_data(**kwargs)
        if 'form' in context:
            del context['form']
        return context


class AddCommentView(LoginRequiredMixin, CreateView):
    """Страница добавления комментария."""

    form_class = CommentForm
    template_name = 'blog/comment.html'

    def form_valid(self, form):
        """
        Если форма правильно заполнена,
        то заполняет поля поста и автора комментария.
        """
        post = get_object_or_404(Post, id=self.kwargs['post_id'])
        form.instance.author = self.request.user
        form.instance.post = post
        return super().form_valid(form)

    def get_success_url(self):
        """Перенаправление после успешного комментирования."""
        return reverse_lazy('blog:post_detail', args=[self.kwargs['post_id']])

    def dispatch(self, request, *args, **kwargs):
        """Перенаправление неавторизованных пользователей."""
        if not request.user.is_authenticated:
            return redirect(reverse('login'))
        return super().dispatch(request, *args, **kwargs)


class EditCommentView(UpdateView):
    """Страница редактирования комментария."""

    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def get_object(self):
        """Получение объекта комментария."""
        comment = get_object_or_404(Comment,
                                    id=self.kwargs['comment_id'],
                                    post_id=self.kwargs['post_id'])
        if comment.author != self.request.user:
            raise Http404("Недостаточно прав для редактирования комментария.")
        return comment

    def get_success_url(self):
        """Перенаправление после успешного комментирования."""
        return reverse_lazy('blog:post_detail', args=[self.object.post.id])


class DeleteCommentView(DeleteView):
    """Страница удаления комментария."""

    model = Comment
    template_name = 'blog/comment.html'

    def get_object(self):
        """Получение комментария."""
        comment = get_object_or_404(Comment,
                                    id=self.kwargs['comment_id'],
                                    post_id=self.kwargs['post_id'])
        if comment.author != self.request.user:
            raise Http404("Недостаточно прав для удаления комментария.")
        return comment

    def get_context_data(self, **kwargs):
        """Удаление формы из контекста."""
        context = super().get_context_data(**kwargs)
        if 'form' in context:
            del context['form']
        return context

    def get_success_url(self):
        """Перенаправление при успешном удалении."""
        return reverse_lazy('blog:post_detail', args=[self.object.post.id])


class ProfileView(PostMixin, ListView):
    """Страница профиля пользователя."""

    paginate_by = PAGES
    model = Post
    template_name = 'blog/profile.html'
    context_object_name = 'post_list'

    def get_queryset(self):
        """
        Получение профиля пользователя и заполнение его постами.
        Автор видит все свои посты, гость видит только опубликованные.
        """
        profile = get_object_or_404(User, username=self.kwargs['username'])
        if self.request.user != profile:
            return super().get_queryset().filter(author=profile,
                                                 category__is_published=True)
        return Post.objects.select_related(
            'category',
            'location',
            'author'
        ).annotate(comment_count=Count('comments')).filter(
            author=profile
        ).order_by('-pub_date')

    def get_context_data(self, **kwargs):
        """Передача профиля в контекст."""
        context = super().get_context_data(**kwargs)
        context['profile'
                ] = get_object_or_404(User, username=self.kwargs['username'])
        return context


class EditProfileView(LoginRequiredMixin, UpdateView):
    """Страница редактирования данных пользователя."""

    model = User
    form_class = UserForm
    template_name = 'blog/user.html'

    def get_object(self):
        """Возвращает пользователя или ошибку 404."""
        return get_object_or_404(User, username=self.request.user.username)

    def get_success_url(self):
        """Перенаправление после успешного редактирования."""
        return reverse_lazy('blog:profile', args=[self.request.user.username])


class RegistrationView(CreateView):
    """Страница регистрации пользователя."""

    template_name = 'registration/registration_form.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('blog:index')

    def form_valid(self, form):
        """При успешной регистрации отправляет письмо пользователю."""
        response = super().form_valid(form)

        send_mail(
            'Добро пожаловать!',
            'Спасибо за регистрацию на нашем сайте.',
            'from@example.com',
            [form.cleaned_data['email']],
        )

        return response


class PasswordResetEmailView(PasswordResetView):
    """Страница смены пароля."""

    def generate_random_password(self, length=8):
        """Генерация случайного пароля."""
        characters = ascii_letters + digits + punctuation
        return ''.join(choice(characters) for i in range(length))

    def form_valid(self, form):
        """Если пользователь запросил смену пароля."""
        email = form.cleaned_data.get('email')

        # Проверка, существует ли пользователь с указанным email.
        user = User.objects.filter(email=email).first()
        if user:
            # Генерация ссылку для сброса пароля.
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = PasswordResetTokenGenerator().make_token(user)
            password_reset_link = self.request.build_absolute_uri(
                reverse('password_reset_confirm',
                        kwargs={'uidb64': uid, 'token': token})
            )

            # Загрузка шаблона письма.
            context = {
                'user': user,
                'url': password_reset_link,
            }
            message = render_to_string(
                'registration/password_reset_email.html',
                context)

            # Отправка письма с ссылкой по данному адресу.
            send_mail(
                subject='Сброс пароля',
                message=message,
                from_email='admin@example.com',
                recipient_list=[email],
                fail_silently=False,
            )
            response = super().form_valid(form)
        else:
            # Если не нашел почту, то сообщает.
            form.add_error(
                'email', (
                    "Пользователь с таким адресом электронной почты не найден."
                )
            )
            response = super().form_invalid()

        return response
