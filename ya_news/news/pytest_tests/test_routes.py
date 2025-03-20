from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'url_key, parametrized_client, status',
    [
        ('home', 'client', HTTPStatus.OK),
        ('login', 'client', HTTPStatus.OK),
        ('logout', 'client', HTTPStatus.OK),
        ('signup', 'client', HTTPStatus.OK),
    ]
)
def test_pages_availability_for_anonymous_user(
        url_key,
        parametrized_client,
        status,
        request,
        url_home
):
    """
    Проверка на доступ к: главной странице, логину, логауту,
    регистрации анонимному пользователю (всем).
    """
    client = request.getfixturevalue(parametrized_client)
    url = url_home[url_key]
    response = client.get(url)
    assert response.status_code == status


@pytest.mark.parametrize( 
    'url_key, parametrized_client, comment_pk',
    [
        (
            'edit',
            'author_client',
            True
        ),
        (
            'delete',
            'author_client',
            True
        ),
    ]
)
def test_pages_availability_for_author(
        url_key,
        parametrized_client,
        request,
        comment_pk
):
    """
    Проверка доступа к редактированию
    и удалению комментария автору комментария.
    """
    client = request.getfixturevalue(parametrized_client)
    comment = request.getfixturevalue('comment')
    url = request.getfixturevalue('reverse_url')[url_key]
    if comment_pk:
        url += f'?id={comment.pk}'
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize("key", ['edit', 'delete'])
def test_redirects(client, reverse_url, login_url, key):
    """Проверка редиректа на страницу логина."""
    url = reverse_url[key]
    expected_url = f"{login_url}?next={url}"
    response = client.get(url)
    assertRedirects(response, expected_url)


@pytest.mark.parametrize(
    'url_key, parametrized_client, comment_pk',
    [
        (
            'edit',
            'not_author_client',
            True
        ),
        (
            'delete',
            'not_author_client',
            True
        ),
    ]
)
def test_pages_availability_for_not_author(
        url_key,
        parametrized_client,
        request,
        comment_pk
):
    """
    Проверка доcтупа к редактированию
    и удалению комментария не автору коментария.
    """
    client = request.getfixturevalue(parametrized_client)
    comment = request.getfixturevalue('comment')
    url = request.getfixturevalue('reverse_url')[url_key]
    if comment_pk:
        url += f'?id={comment.pk}'
    response = client.get(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    
