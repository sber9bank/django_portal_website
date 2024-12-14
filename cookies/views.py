from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView, DetailView, CreateView, RedirectView, FormView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.db.models import F, Q

from .models import Category, Post, PostView, Comment, Profile
from .forms import PostAddForm, LoginForm, RegistrationForm, CommentForm, ProfileForm
from cookies.utils import get_client_ip

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

# 1. Главная страница — Список опубликованных постов
class IndexView(ListView):
    model = Post
    template_name = 'cookies/index.html'
    context_object_name = 'posts'
    queryset = Post.objects.filter(is_published=True).order_by('-published_date')  # Убедитесь, что 'published_date' есть в Post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Кулинарный портал'
        context['categories'] = Category.objects.all()
        return context

# 2. Список постов по категории
class CategoryListView(IndexView):

    def get_queryset(self):
        self.category = get_object_or_404(Category, pk=self.kwargs['pk'])
        return Post.objects.filter(category=self.category, is_published=True).order_by('-published_date')  # Проверьте наличие 'published_date'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Категория: {self.category.title}'
        context['categories'] = Category.objects.all()
        return context

# 3. Детали поста с учётом просмотров
class PostDetailView(DetailView):
    model = Post
    template_name = 'cookies/post_detail.html'
    context_object_name = 'post'

    def get_object(self, queryset=None):
        obj = get_object_or_404(Post, pk=self.kwargs['pk'], is_published=True)
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.object
        client_ip = get_client_ip(self.request)

        # Проверяем, существует ли уже запись о просмотре поста этим IP
        view_exists = PostView.objects.filter(post=post, ip_address=client_ip).exists()
        ext_post = Post.objects.exclude(pk=post.pk).order_by('-watched')[:5]

        if not view_exists:
            # Если записи нет, увеличиваем счетчик и создаем новую запись
            Post.objects.filter(pk=post.pk).update(watched=F('watched') + 1)
            PostView.objects.create(post=post, ip_address=client_ip)

        # Получение комментариев
        comments = Comment.objects.filter(post=post, is_published=True).order_by('-created_at')

        # Увеличение счётчика просмотров для каждого комментария
        for comment in comments:
            Comment.objects.filter(pk=comment.pk).update(watched=F('watched') + 1)

        context['title'] = post.title
        context['ext_posts'] = ext_post
        # Исправлено: сортировка по '-created_at' вместо '-published_date'
        context['comments'] = Comment.objects.filter(post=post, is_published=True).order_by('-created_at')
        if self.request.user.is_authenticated:
            context['comment_form'] = CommentForm()
        return context

# 4. Добавление нового поста
class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostAddForm
    template_name = 'cookies/components/_add_post.html'
    extra_context = {'title': 'Добавить статью'}

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


# 5. Изменение поста
class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostAddForm
    template_name = 'cookies/components/_add_post.html'
    extra_context = {"title": 'Изменение статьи'}

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author


# 6. Удаление поста
class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    success_url = reverse_lazy('home')
    context_object_name = 'post'
    extra_context = {"title": 'Удаление статьи'}


# 7. Авторизация пользователя
class UserLoginView(FormView):
    form_class = LoginForm
    template_name = 'cookies/components/_login_form.html'
    success_url = reverse_lazy('home')
    extra_context = {'title': 'Авторизация пользователя'}

    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)
        messages.success(self.request, 'Вы успешно авторизовались!')
        return super().form_valid(form)


# 8. Выход пользователя
class UserLogoutView(RedirectView):
    url = reverse_lazy('home')

    def get(self, request, *args, **kwargs):
        logout(request)
        return super().get(request, *args, **kwargs)

# 9. Регистрация пользователя
def register(request):
    if request.method == 'POST':
        user_form = RegistrationForm(request.POST)
        profile_form = ProfileForm(request.POST, request.FILES)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            user.save()
            # Профиль создаётся через сигналы
            profile = user.profile
            profile_form = ProfileForm(request.POST, request.FILES, instance=profile)
            if profile_form.is_valid():
                profile_form.save()

            # Аутентификация и вход пользователя
            username = user_form.cleaned_data.get('username')
            raw_password = user_form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)

            if user is not None:
                login(request, user)
                messages.success(request, 'Регистрация прошла успешно! Добро пожаловать.')
                return redirect('profile', identifier=username)
            else:
                messages.error(request, 'Ошибка аутентификации. Попробуйте войти.')
                return redirect('login')
    else:
        user_form = RegistrationForm()
        profile_form = ProfileForm()

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'cookies/components/_register_form.html', context)

# 10. Поиск в статьях и содержимом
class SearchView(IndexView):

    def get_queryset(self):
        word = self.request.GET.get('q')
        if not word:
            return Post.objects.none()
        return Post.objects.filter(
            Q(title__icontains=word) | Q(content__icontains=word),
            is_published=True
        ).order_by('-published_date')

# Обработчик добавления комментария

def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id, is_published=True)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.user = request.user
        comment.post = post
        comment.save()
        messages.success(request, 'Ваш комментарий успешно добавлен!')

    return redirect('post_detail', pk=post_id)

# Профиль
def profile_view(request, identifier):
    """
    Представление для отображения профиля пользователя по ID или username.
    :param request: HTTP запрос.
    :param identifier: ID пользователя или его username.
    """
    try:
        # Попробуем интерпретировать идентификатор как integer (user_id)
        user_id = int(identifier)
        user = User.objects.get(pk=user_id)
    except (ValueError, User.DoesNotExist):
        # Если не удалось, рассматриваем как username
        user = get_object_or_404(User, username=identifier)

    posts = Post.objects.filter(author=user, is_published=True).order_by('-published_date')
    context = {
        'user_profile': user,
        'posts': posts,
    }
    return render(request, 'cookies/components/_profile.html', context)

# Обработчики лайков и дизлайков
@login_required
def like_comment(request, comment_id):
    if request.method == 'POST':
        comment = get_object_or_404(Comment, id=comment_id)
        user = request.user

        if comment.likes.filter(id=user.id).exists():
            comment.likes.remove(user)
            liked = False
        else:
            comment.likes.add(user)
            comment.dislikes.remove(user)
            liked = True

        return JsonResponse({
            'likes_count': comment.likes_count,
            'dislikes_count': comment.dislikes_count,
            'liked': liked
        })
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def dislike_comment(request, comment_id):
    if request.method == 'POST':
        comment = get_object_or_404(Comment, id=comment_id)
        user = request.user

        if comment.dislikes.filter(id=user.id).exists():
            comment.dislikes.remove(user)
            disliked = False
        else:
            comment.dislikes.add(user)
            comment.likes.remove(user)
            disliked = True

        return JsonResponse({
            'likes_count': comment.likes_count,
            'dislikes_count': comment.dislikes_count,
            'disliked': disliked
        })
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def edit_profile(request, username):
    user_profile = get_object_or_404(User, username=username)

    if request.user != user_profile:
        messages.error(request, "У вас нет прав на редактирование этого профиля.")
        return redirect('profile', username=username)

    try:
        profile = user_profile.profile
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=user_profile)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Ваш профиль успешно обновлен.")
            return redirect('profile', identifier=username)
    else:
        form = ProfileForm(instance=profile)

    context = {
        'form': form,
        'user_profile': user_profile,
    }
    return render(request, 'cookies/components/_edit_profile.html', context)
