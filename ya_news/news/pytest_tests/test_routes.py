from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'reverse_url, parametrized_client, status',
    [
        ('news:home', 'client', HTTPStatus.OK),
        ('users:login', 'client', HTTPStatus.OK),
        ('users:logout', 'client', HTTPStatus.OK),
        ('users:signup', 'client', HTTPStatus.OK),
    ]
)
def test_pages_availability_for_anonymous_user(
        reverse_url,
        parametrized_client,
        status,
        request
):
    """
    Проверка на доступ к: главной странцие, логин, логаут,
    регистрации, отдельной новости анонимному пользователю(всем).
    """
    client = request.getfixturevalue(parametrized_client)
    url = reverse(reverse_url)
    response = client.get(url)
    assert response.status_code == status


def test_pages_availability_for_author(
        author_client,
        reverse_url,
):
    """
    Проверка доcтупа к редактированию
    и удалению комментария автору коментария.
    """
    for key, url in reverse_url.items():
        response = author_client.get(url)
        assert response.status_code == HTTPStatus.OK


def test_redirects(client, reverse_url, login_url):
    """Проверка редиректа на страницу логина."""
    for key, url in reverse_url.items():
        expected_url = f"{login_url}?next={url}"
        response = client.get(url)
        assertRedirects(response, expected_url)


@pytest.mark.parametrize(
    'reverse_url, parametrized_client, status',
    [
        ('news:edit', 'not_author_client', HTTPStatus.NOT_FOUND),
        ('news:delete', 'not_author_client', HTTPStatus.NOT_FOUND),
    ]
)
def test_pages_availability_for_author(
        reverse_url,
        parametrized_client,
        status,
        request
):
    """
    Проверка доcтупа к редактированию
    и удалению комментария не автору коментария.
    """
    client = request.getfixturevalue(parametrized_client)
    response = client.get(reverse_url)
    assert response.status_code == status
