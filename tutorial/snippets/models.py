from django.db import models
from pygments.lexers import get_all_lexers
from pygments.styles import get_all_styles

from pygments.lexers import get_lexer_by_name
from pygments.formatters.html import HtmlFormatter
from pygments import highlight

from django.conf import settings
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.contrib import admin
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.models import TokenUser

LEXERS = [item for item in get_all_lexers() if item[1]]
LANGUAGE_CHOICES = sorted([(item[1][0], item[0]) for item in LEXERS])
STYLE_CHOICES = sorted([(item, item) for item in get_all_styles()])


class Snippet(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100, blank=True, default='')
    code = models.TextField()
    linenos = models.BooleanField(default=False)
    language = models.CharField(
        choices=LANGUAGE_CHOICES, default='python', max_length=100)
    style = models.CharField(choices=STYLE_CHOICES,
                             default='friendly', max_length=100)
    owner = models.ForeignKey(
        'auth.User', related_name='snippets', on_delete=models.CASCADE)
    highlighted = models.TextField()

    class Meta:
        ordering = ['created']

    def save(self, *args, **kwargs):
        """
        Use the `pygments` library to create a highlighted HTML
        representation of the code snippet.
        """
        lexer = get_lexer_by_name(self.language)
        linenos = 'table' if self.linenos else False
        options = {'title': self.title} if self.title else {}
        formatter = HtmlFormatter(style=self.style, linenos=linenos,
                                  full=True, **options)
        self.highlighted = highlight(self.code, lexer, formatter)
        super(Snippet, self).save(*args, **kwargs)


@admin.register(Snippet)
class SnippetAdmin(admin.ModelAdmin):
    list_display = ['title', 'owner']


class Task(models.Model):
    title = models.CharField(max_length=100, blank=True, default='')
    code = models.TextField()

    class Meta:
        permissions = [
            ("change_task_status", "Can change the status of tasks"),
            ("close_task", "Can remove a task by setting its status as closed"),
        ]


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class Topping(models.Model):
    name = models.CharField(max_length=200)
    created = models.DateField(auto_now_add=True)

    def __str__(self) -> str:
        return self.name


@ admin.register(Topping)
class ToppingAdmin(admin.ModelAdmin):
    list_display = ['name', 'created']
    list_display_links = ['name']


class Pizza(models.Model):
    name = models.CharField(max_length=255)
    toppings = models.ManyToManyField(Topping)


@admin.register(Pizza)
class PizzaAdmin(admin.ModelAdmin):
    list_display = ['name']


class Article(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self) -> str:
        return self.name


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['name']


class Tag(models.Model):
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name="tags",
        related_query_name="tag",
    )
    name = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.name


@ admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']
# That's now the name of the reverse filter
# Article.objects.filter(tag__name="important")
