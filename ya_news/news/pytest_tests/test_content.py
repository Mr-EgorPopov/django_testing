from http import HTTPStatus

import pytest
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from news.forms import CommentForm

pytestmark = pytest.mark.django_db


def test_anon_user_cannot_access_comment_form(news, client, url_detail):
    """Проверка на то, что форма комментария не доступна для анонима."""
    response = client.get(url_detail)
    assert response.status_code == HTTPStatus.OK
    assert 'form' not in response.context


def test_auth_user_can_access_comment_form(news, author_client, url_detail):
    """
    Проверка на то, что форма комментария
    доступна для залогиненного юзера.
    """
    response = author_client.get(url_detail)
    form = response.context['form']
    assert response.status_code == HTTPStatus.OK
    assert 'form' in response.context
    assert isinstance(form, CommentForm)


def test_value_news(client, create_news, news, url_detail):
    """Проверка на кол-во новостей на главной странице и их сортировку."""
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    assert settings.NEWS_COUNT_ON_HOME_PAGE == len(object_list)
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


def test_comment_news(client, create_comments, news, url_detail):
    """Проверка сортировки комментариев."""
    response = client.get(url_detail)
    news = response.context['news']
    all_comments = list(news.comment_set.all())
    assert isinstance(all_comments[0].created, timezone.datetime)
    assert all_comments == sorted(all_comments, key=lambda x: x.created)
