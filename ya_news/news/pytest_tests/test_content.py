import pytest
from django.conf import settings
from django.utils import timezone
from django.urls import reverse


@pytest.mark.django_db
def test_anon_user_cannot_access_comment_form(news, client):
    """Проверка на то, что форма комментария не доступна для анонима."""
    url = reverse('news:detail', args=(news.pk,))
    response = client.get(url)
    assert response.status_code == 200
    assert 'form' not in response.context


@pytest.mark.django_db
def test_auth_user_can_access_comment_form(news, author_client):
    """
    Проверка на то, что форма комментария
    доступна для залогиненного юзера.
    """
    url = reverse('news:detail', args=(news.pk,))
    response = author_client.get(url)
    assert response.status_code == 200
    assert 'form' in response.context


@pytest.mark.django_db
def test_value_news(client, create_news):
    """Проверка на кол-во новостей на главной странице и их сортировку."""
    url = reverse('news:home')
    response = client.get(url)
    news_count = response.context['object_list']
    assert int(settings.NEWS_COUNT_ON_HOME_PAGE) == len(news_count)
    for news_true, news_try in zip(
        news_count, sorted(news_count, key=lambda x: x.date)
    ):
        assert news_true.date == news_try.date


@pytest.mark.django_db
def test_comment_news(client, create_comments, news):
    """Проверка сортировки комментариев."""
    url = reverse('news:detail', args=(news.pk,))
    response = client.get(url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = list(news.comment_set.all())
    assert isinstance(all_comments[0].created, timezone.datetime)
    assert all_comments == sorted(all_comments, key=lambda x: x.created)
