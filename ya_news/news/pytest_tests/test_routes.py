from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects

pytestmark = pytest.mark.django_db


def test_pages_availability_for_anonymous_user(
        client,
        url_detail,
        url_home
):
    """
    Проверка на доступ к: главной странцие, логин, логаут,
    регистрации, отдельной новости анонимному пользователю(всем).
    """
    for key, url in url_home.items():
        response = client.get(url)
        assert response.status_code == HTTPStatus.OK
        response_detail = client.get(url_detail)
        assert response_detail.status_code == HTTPStatus.OK


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


def test_redirects(client, reverse_url):
    """Проверка редиректа на страницу логина."""
    login_url = reverse('users:login')
    for key, url in reverse_url.items():
        expected_url = f"{login_url}?next={url}"
        response = client.get(url)
        assertRedirects(response, expected_url)


def test_pages_availability_for_author(
    not_author_client,
    reverse_url
):
    """
    Проверка доcтупа к редактированию
    и удалению комментария не автору коментария.
    """
    # Я не понимать про обьеденение тестов на статусы...
    for key, url in reverse_url.items():
        response = not_author_client.get(url)
        assert response.status_code == HTTPStatus.NOT_FOUND
