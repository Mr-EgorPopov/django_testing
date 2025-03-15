from http import HTTPStatus

import pytest
from django.urls import reverse

from news.forms import BAD_WORDS, WARNING

FORM_DATA = {'text': 'Текст комментария'}

pytestmark = pytest.mark.django_db


def test_anonymous_user_cant_create_comment(news, client, url_detail):
    """Проверка на создание комментаря анонимным пользователем."""
    response_get = client.get(url_detail)
    comments_count_before = response_get.context['news'].comment_set.count()
    client.post(url_detail, data=FORM_DATA)
    response_get = client.get(url_detail)
    comments_count_after = response_get.context['news'].comment_set.count()
    assert comments_count_before == comments_count_after


def test_user_can_create_comment(news, author_client, url_detail):
    """
    Проверка на создание комментаря авторизированным пользователем
    и использование запрещенных слов
    """
    bad_words_data = {'text': f'{BAD_WORDS[0]}'}
    author_client.post(url_detail, data=FORM_DATA)
    response_bad_word = author_client.post(url_detail, data=bad_words_data)
    form = response_bad_word.context['form']
    response_get = author_client.get(url_detail)
    object_list = response_get.context['news']
    comments_count = object_list.comment_set.count()
    assert comments_count == 1
    assert WARNING in form.errors['text']


def test_author_can_delete_comment(author_client, comment, news, url_detail):
    """
    Проверка на возможность редактирования комментария
    авторизированным пользователем.
    """
    comment_edit = {'text': 'Отредактировано'}
    url_edit = reverse('news:edit', args=(comment.pk,))
    author_client.post(url_edit, data=comment_edit)
    response_get = author_client.get(url_detail)
    object_list = response_get.context['news']
    comment_text = object_list.comment_set.get(id=comment.id)
    assert comment_edit['text'] == comment_text.text


def test_author_can_delete_comment(author_client, comment, news, url_detail):
    """
    Проверка на возможность удаления комментария
    авторизированным пользователем.
    """
    url_delete = reverse('news:delete', args=(comment.pk,))
    response_get = author_client.get(url_detail)
    object_list = response_get.context['news']
    comments_count_before = object_list.comment_set.count()
    author_client.delete(url_delete)
    response_get = author_client.get(url_detail)
    object_list = response_get.context['news']
    comments_count_after = object_list.comment_set.count()
    assert comments_count_after == comments_count_before - 1


def test_not_author_can_delete_comment(
        not_author_client,
        comment,
        news,
        url_detail
):
    """
    Проверка на не возможность редактирования комментария
    чужих комментариев.
    """
    comment_edit = {'text': 'Отредактировано'}
    url_edit = reverse('news:edit', args=(comment.pk,))
    response_edit = not_author_client.post(url_edit, data=comment_edit)
    assert response_edit.status_code == HTTPStatus.NOT_FOUND
    response_get = not_author_client.get(url_detail)
    object_list = response_get.context['news']
    comment_text = object_list.comment_set.get(pk=comment.pk)
    assert comment.text == comment_text.text
    assert comment.author == comment_text.author


def test_not_author_can_delete_comment(
        not_author_client,
        comment,
        news,
        url_detail
):
    """
    Проверка на не возможность удаления комментария
    чужих комментариев.
    """
    url_delete = reverse('news:delete', args=(comment.pk,))
    response_get = not_author_client.get(url_detail)
    object_list = response_get.context['news']
    comments_count_before = object_list.comment_set.count()
    response_post = not_author_client.delete(url_delete)
    assert response_post.status_code == HTTPStatus.NOT_FOUND
    comments_count_after = object_list.comment_set.count()
    assert comments_count_before == comments_count_after
