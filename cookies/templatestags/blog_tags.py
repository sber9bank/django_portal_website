from django import template
from cookies.models import Category
from django.db.models import Count, Q

register = template.Library()

@register.simple_tag
def get_all_categories():
    return Category.objects.annotate(cnt=Count('posts', filter=Q(posts__is_published=True))).filter(cnt__gt=0)

    # return Category.objects.all()
    # return Category.objects.annotate(cnt=Count('posts')).filter(cnt__gt=0)
