from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestNoteRoutes(TestCase):
    """Тест доступа главной страницы."""

    @classmethod
    def setUpTestData(cls):
        """Создание заметки."""
        cls.author = User.objects.create(username='testuser')
        cls.anon = User.objects.create(username='anonuser')
        cls.note = Note.objects.create(
            title='Заголовок', text='Текст', author=cls.author
        )
        cls.urls_home = (
            ('notes:home', None),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        )
        cls.url_edit = (
            'notes:edit',
            'notes:delete',
            'notes:detail',
        )
        cls.url_list = (
            'notes:list',
            'notes:success',
            'notes:detail',
            'notes:edit',
            'notes:delete',
        )
        cls.url_add = (
            ('notes:add', None),
            ('notes:success', None),
            ('notes:list', None),
        )

    def user_login(self, user):
        self.client.force_login(user)

    def test_pages_availability(self):
        """Проверка домашней страницы и доступа."""
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.anon, HTTPStatus.OK),
        )
        for user, status in users_statuses:
            for name, args in self.urls_home:
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=args)
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_edit_and_delete(self):
        """Проверка редактирования, удаления заметки."""
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.anon, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            for name in self.url_edit:
                with self.subTest(user=user, name=name):
                    self.user_login(user)
                    url = reverse(name, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        """Проверка на редирект."""
        login_url = reverse('users:login')
        for name in self.url_list:
            with self.subTest(name=name):
                if name in self.url_edit:
                    url = reverse(name, args=(self.note.slug,))
                else:
                    url = reverse(name)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_pages_autentification(self):
        """Проверка доступа списка, добавления заметки."""
        users_statuses = ((self.author, HTTPStatus.OK),)
        for user, status in users_statuses:
            for name, args in self.url_add:
                with self.subTest(user=user, name=name):
                    self.user_login(user)
                    url = reverse(name, args=args)
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, HTTPStatus.OK)
