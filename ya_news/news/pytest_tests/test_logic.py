from http import HTTPStatus

import pytest

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

FORM_DATA = {'text': 'Текст комментария'}

pytestmark = pytest.mark.django_db


def test_anonymous_user_cant_create_comment(client, url_detail):
    """Проверка на создание комментаря анонимным пользователем."""
    comments_count_before = Comment.objects.count()
    client.post(url_detail, data=FORM_DATA)
    comments_count_after = Comment.objects.count()
    assert comments_count_before == comments_count_after


def test_user_can_create_comment(author_client, url_detail):
    """
    Проверка на создание комментаря авторизированным пользователем
    и использование запрещенных слов
    """
    bad_words_data = {'text': f'{BAD_WORDS[0]}'}
    author_client.post(url_detail, data=FORM_DATA)
    comments_count_before = Comment.objects.count()
    response_bad_word = author_client.post(url_detail, data=bad_words_data)
    form = response_bad_word.context['form']
    comments_count_after = Comment.objects.count()
    assert comments_count_after == comments_count_before
    assert WARNING in form.errors['text']


def test_author_can_edit_comment(
        author_client,
        comment,
        url_edit
):
    """
    Проверка на возможность редактирования комментария
    авторизированным пользователем.
    """
    comment_edit = {'text': 'Отредактировано'}
    author_client.post(url_edit, data=comment_edit)
    updated_comment = Comment.objects.get(id=comment.id)
    assert comment_edit['text'] == updated_comment.text
    assert updated_comment.author == comment.author
    assert comment.news == updated_comment.news


def test_author_can_delete_comment(
        author_client,
        url_delete
):
    """
    Проверка на возможность удаления комментария
    авторизированным пользователем.
    """
    comments_count_before = Comment.objects.count()
    author_client.delete(url_delete)
    comments_count_after = Comment.objects.count()
    assert comments_count_after == comments_count_before - 1


def test_not_author_can_delete_comment(
        not_author_client,
        comment,
        url_edit,
):
    """
    Проверка на невозможность
    редактирования чужого комментария.
    """
    comment_edit = {'text': 'Отредактировано'}
    response_edit = not_author_client.post(url_edit, data=comment_edit)
    assert response_edit.status_code == HTTPStatus.NOT_FOUND
    updated_comment = Comment.objects.get(pk=comment.pk)
    assert comment.text == updated_comment.text
    assert comment.author == updated_comment.author
    assert comment.news == updated_comment.news


def test_not_author_can_delete_comment(
        not_author_client,
        url_delete
):
    """
    Проверка на невозможность
    удаления чужого комментария.
    """
    comments_count_before = Comment.objects.count()
    response_post = not_author_client.delete(url_delete)
    assert response_post.status_code == HTTPStatus.NOT_FOUND
    comments_count_after = Comment.objects.count()
    assert comments_count_before == comments_count_after
