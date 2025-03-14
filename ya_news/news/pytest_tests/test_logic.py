from http import HTTPStatus

import pytest
from django.conf import settings
from django.urls import reverse
from news.forms import BAD_WORDS

FORM_DATA = {'text': 'Текст комментария'}

@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(news, client):
    """
    Проверка на создание комментаря анонимным пользователем.
    """
    url = reverse('news:detail', args=(news.pk,))
    response_post = client.post(url, data=FORM_DATA)
    response_get = client.get(url)
    object_list = response_get.context['news']
    comments_count = object_list.comment_set.count()
    assert comments_count == 0

@pytest.mark.django_db
def test_user_can_create_comment(news, author_client):
    """
    Проверка на создание комментаря авторизированным пользователем 
    и использование запрещенных слов
    """
    bad_words_data = {'text': f'{BAD_WORDS[0]}'}
    url = reverse('news:detail', args=(news.pk,))
    response_post = author_client.post(url, data=FORM_DATA)
    response_bad_word = author_client.post(url, data=bad_words_data)
    form = response_bad_word.context['form']
    response_get = author_client.get(url)
    object_list = response_get.context['news']
    comments_count = object_list.comment_set.count()
    assert 'Не ругайтесь!' in form.errors['text']
    assert comments_count == 1

def test_author_can_delete_comment(author_client, comment, news):
    """
    Проверка на возможность редактирования и удаления комментария
    авторизированным пользователем.
    """
    comment_edit = {'text': f'Отредактировано'}
    url_edit = reverse('news:edit', args=(news.pk,))
    url_delete = reverse('news:delete', args=(news.pk,))
    url_news = reverse('news:detail', args=(news.pk,))
    response_edit = author_client.post(url_edit, data=comment_edit)
    response_get = author_client.get(url_news)
    object_list = response_get.context['news']
    comment_text = object_list.comment_set.first()
    assert 'Отредактировано' == comment_text.text
    response_delete = author_client.delete(url_delete)
    response_get = author_client.get(url_news)
    object_list = response_get.context['news']
    comments_count = object_list.comment_set.count()
    assert comments_count == 0

def test_not_author_can_delete_comment(not_author_client, comment, news):
    """
    Проверка на не возможность редактирования и удаления комментария
    чужих комментариев.
    """
    comment_edit = {'text': f'Отредактировано'}
    url_edit = reverse('news:edit', args=(news.pk,))
    url_delete = reverse('news:delete', args=(news.pk,))
    url_news = reverse('news:detail', args=(news.pk,))
    response_edit = not_author_client.post(url_edit, data=comment_edit)
    assert response_edit.status_code == HTTPStatus.NOT_FOUND
    response_get = not_author_client.get(url_news)
    object_list = response_get.context['news']
    comment_text = object_list.comment_set.first()
    assert 'Текст комментария' == comment_text.text
    response_post = not_author_client.delete(url_delete)
    assert response_post.status_code == HTTPStatus.NOT_FOUND
    object_list = response_get.context['news']
    comments_count = object_list.comment_set.count()
    assert comments_count == 1