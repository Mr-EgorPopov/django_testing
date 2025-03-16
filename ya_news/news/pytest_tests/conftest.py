from datetime import datetime, timedelta

import pytest
from django.conf import settings
from django.test.client import Client
from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News

TODAY = datetime.today()


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username="Автор")


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username="Не автор")


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news():
    news = News.objects.create(
        title="Заголовок",
        text="Текст комментария",
    )
    return news


@pytest.fixture
def comment(news, author):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text="Текст комментария",
    )
    return comment


@pytest.fixture
def create_news():
    """Фикстура для создания новостей."""
    news_list = [
        News(
            title=f"Заголовок {i}",
            text=f"Текст новости {i}",
            date=TODAY - timedelta(days=i)) for i in range(
                settings.NEWS_COUNT_ON_HOME_PAGE + 1
        )
    ]
    News.objects.bulk_create(news_list)


@pytest.fixture
def create_comments(news, author):
    """Фикстура для создания комментариев."""
    comment_list = []
    for i in range(settings.NEWS_COUNT_ON_HOME_PAGE):
        comment = Comment(
            news=news,
            author=author,
            text=f"Текст комментария {i}",
        )
        comment.save()
        comment.created = timezone.now() - timedelta(days=i)
        comment.save()
        comment_list.append(comment)
    return comment_list


@pytest.fixture
def url_detail(news):
    """Фикстура для реверса отдельной новости."""
    return reverse('news:detail', args=(news.pk,))


@pytest.fixture
def url_home():
    """
    Возвращает реверсы для главной страницы,
    логина, логаута и регистрации.
    """
    return {
        'home': reverse('news:home'),
        'login': reverse('users:login'),
        'logout': reverse('users:logout'),
        'signup': reverse('users:signup'),
    }


@pytest.fixture
def reverse_url(comment):
    return {
        'delete': reverse('news:delete', args=(comment.pk,)),
        'edit': reverse('news:edit', args=(comment.pk,))
    }


@pytest.fixture
def url_edit(comment):
    return reverse('news:edit', args=(comment.pk,))


@pytest.fixture
def url_delete(comment):
    return reverse('news:delete', args=(comment.pk,))


@pytest.fixture
def url_edit(comment):
    return reverse('news:edit', args=(comment.pk,))
