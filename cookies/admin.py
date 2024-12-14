from django.contrib import admin
from .models import Category, Post, Comment, PostView, Profile
from django.utils.html import mark_safe

class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'published_date', 'watched', 'is_published')
    list_filter = ('is_published', 'category', 'author')
    search_fields = ('title', 'content', 'author__username')
    ordering = ('-published_date',)
    raw_id_fields = ('author',)
    autocomplete_fields = ('author',)
    list_per_page = 25


    def display_image(self, obj):
        if obj.image and hasattr(obj.image, 'url'):
            return mark_safe(
                f'<a href="{obj.image.url}" '
                f'onclick="window.open(this.href, \'popup\', \'width=800,height=600,scrollbars=yes\'); return false;">'
                f'<img src="{obj.image.url}" width="90" height="90" style="object-fit: cover;" />'
                f'</a>'
            )
        return "-"

    display_image.short_description = 'Изображение'

admin.site.register(Category)
admin.site.register(Post, PostAdmin)
admin.site.register(Comment)
admin.site.register(PostView)
admin.site.register(Profile)