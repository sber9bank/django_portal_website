from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse


User = get_user_model()

# Добавление модели Profile
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name='Пользователь')
    avatar = models.ImageField(upload_to='avatars/%Y/', blank=True, null=True, verbose_name='Аватар')
    bio = models.TextField(max_length=500, blank=True, null=True, verbose_name='Биография')
    job_title = models.CharField(max_length=255, blank=True, null=True, verbose_name='Должность')
    website = models.URLField(max_length=200, blank=True, null=True, verbose_name='Вебсайт')
    github = models.URLField(max_length=200, blank=True, null=True, verbose_name='Github')
    instagram = models.URLField(max_length=200, blank=True, null=True, verbose_name='Instagram')
    facebook = models.URLField(max_length=200, blank=True, null=True, verbose_name='Facebook')
    whatsapp = models.CharField(max_length=20, blank=True, null=True, verbose_name='WhatsApp')
    telegram_username = models.CharField(max_length=50, blank=True, null=True, verbose_name='Telegram Username')
    country = models.CharField(max_length=100, blank=True, null=True, verbose_name='Страна')

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'

    def __str__(self):
        return f'Профиль пользователя {self.user.username}'

    def get_absolute_url(self):
        return reverse('profile', kwargs={'username': self.user.username})

class Category(models.Model):
    title = models.CharField(max_length=255, verbose_name='Заголовок Категории')

    class Meta:
        verbose_name = "Категорию"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('category_list', kwargs={'pk': self.pk})
    
class Post(models.Model):
    title = models.CharField(max_length=255, verbose_name='Заголовок статьи')
    content = models.TextField(default='Скоро тут будет статья...', verbose_name='Текст статьи')
    published_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации:')
    update_date = models.DateTimeField(auto_now=True, verbose_name='Дата обновления:')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Категория')
    image = models.ImageField(upload_to='post_images/%Y/', blank=True, null=True, verbose_name='Картинка Статьи')
    watched = models.IntegerField(default=0, verbose_name='Просмотры:')
    is_published = models.BooleanField(default=True, verbose_name='Публикация')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts', verbose_name='Автор', null=True, blank=True)


    class Meta:
        verbose_name = "Запись"
        verbose_name_plural = "Записи"
        ordering = ['-published_date']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post_detail', kwargs={'pk': self.pk})


class PostView(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='views')
    ip_address = models.GenericIPAddressField()
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'IP Лог'
        verbose_name_plural = 'IP Логи'
        unique_together = ('post', 'ip_address')  # Обеспечивает уникальность пары пост-IP

    def __str__(self):
        return f"IP:{self.ip_address} Смотрел: {self.post.title}"


class Comment(models.Model):
    post = models.ForeignKey(
        'Post',
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Пост'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Пользователь'
    )
    text = models.TextField(verbose_name='Комментарий')
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )
    is_published = models.BooleanField(
        default=True,
        verbose_name='Публикация'
    )
    watched = models.PositiveIntegerField(
        default=0,
        verbose_name='Просмотры'
    )
    likes = models.ManyToManyField(
        User,
        related_name='liked_comments',
        blank=True,
        verbose_name='Лайки'
    )
    dislikes = models.ManyToManyField(
        User,
        related_name='disliked_comments',
        blank=True,
        verbose_name='Дизлайки'
    )

    def __str__(self):
        return f'Комментарий от {self.user.username} к посту {self.post.title}'

    @property
    def likes_count(self):
        return self.likes.count()

    @property
    def dislikes_count(self):
        return self.dislikes.count()

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['post', 'created_at']),
            models.Index(fields=['user']),
        ]
