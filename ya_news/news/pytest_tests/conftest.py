import pytest
from django.conf import settings
from django.test.client import Client
from news.models import Comment, News


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


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
        title='Заголовок',
        text='Текст комментария',
    )
    return news

@pytest.fixture
def comment(news, author):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария',
    )
    return comment

@pytest.fixture
def create_news():
    """Фикстура для создания 10 новостей."""
    news_list = [
        News(
            title=f'Заголовок {i}',
            text=f'Текст новости {i}'
        ) for i in range(10)
    ]
    News.objects.bulk_create(news_list)
    return news_list

@pytest.fixture
def create_comments(news, author):
    """Фикстура для создания 10 комментариев."""
    comment_list = [
        Comment(
            news=news,
            author=author,
            text=f'Текст комментария {i}',
        ) for i in range(settings.NEWS_COUNT_ON_HOME_PAGE)

    ]
    Comment.objects.bulk_create(comment_list)
    return comment_list
