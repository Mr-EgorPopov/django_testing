from http import HTTPStatus

import pytest
from django.urls import reverse
from news.models import News
from pytest_django.asserts import assertRedirects


@pytest.mark.django_db
def test_empty_db():
    notes_count = News.objects.count()
    assert notes_count == 0


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name', ('news:home', 'users:login', 'users:logout', 'users:signup')
)
def test_pages_availability_for_anonymous_user(client, name, news):
    """
    Проверка на доступ к: главной странцие, логин, логаут,
    регистрации, отдельной новости анонимному пользователю(всем).
    """
    url = reverse(name)
    url1 = reverse('news:detail', args=(news.pk,))
    response = client.get(url)
    response1 = client.get(url1)
    assert response.status_code == HTTPStatus.OK
    assert response1.status_code == HTTPStatus.OK


@pytest.mark.django_db
@pytest.mark.parametrize('name', ('news:delete', 'news:edit'))
def test_pages_availability_for_author(author_client, name, comment):
    """
    Проверка доcтупа к редактированию
    и удалению комментария автору коментария.
    """
    url = reverse(name, args=(comment.pk,))
    response = author_client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
@pytest.mark.parametrize('name', ('news:edit', 'news:delete'))
def test_redirects(client, name, comment):
    """Проверка редиректа на страницу логина."""
    login_url = reverse('users:login')
    url = reverse(name, args=(comment.pk,))
    expected_url = f"{login_url}?next={url}"
    response = client.get(url)
    assertRedirects(response, expected_url)


@pytest.mark.django_db
@pytest.mark.parametrize('name', ('news:delete', 'news:edit'))
def test_pages_availability_for_author(not_author_client, name, comment):
    """
    Проверка доcтупа к редактированию
    и удалению комментария автору коментария.
    """
    url = reverse(name, args=(comment.pk,))
    response = not_author_client.get(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
