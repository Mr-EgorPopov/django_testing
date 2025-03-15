from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects

pytestmark = pytest.mark.django_db


def test_pages_availability_for_anonymous_user(
        client,
        news,
        url_detail,
        url_home
):
    """
    Проверка на доступ к: главной странцие, логин, логаут,
    регистрации, отдельной новости анонимному пользователю(всем).
    """
    for adress in url_home:
        url = reverse(adress)
        response = client.get(url)
        response1 = client.get(url_detail)
        assert response.status_code == HTTPStatus.OK
        assert response1.status_code == HTTPStatus.OK


def test_pages_availability_for_author(
        author_client,
        comment,
        url_del_edit
):
    """
    Проверка доcтупа к редактированию
    и удалению комментария автору коментария.
    """
    for adress in url_del_edit:
        url = reverse(adress, args=(comment.pk,))
        response = author_client.get(url)
        assert response.status_code == HTTPStatus.OK


def test_redirects(client, comment, url_del_edit):
    """Проверка редиректа на страницу логина."""
    login_url = reverse('users:login')
    for adress in url_del_edit:
        url = reverse(adress, args=(comment.pk,))
        expected_url = f"{login_url}?next={url}"
        response = client.get(url)
        assertRedirects(response, expected_url)


def test_pages_availability_for_author(
    not_author_client,
    comment,
    url_del_edit
):
    """
    Проверка доcтупа к редактированию
    и удалению комментария автору коментария.
    """
    for adress in url_del_edit:
        url = reverse(adress, args=(comment.pk,))
        response = not_author_client.get(url)
        assert response.status_code == HTTPStatus.NOT_FOUND
