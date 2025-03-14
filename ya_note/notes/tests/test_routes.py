from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):
    """Тест доступа главной страницы."""

    @classmethod
    def setUpTestData(cls):
        """Создание заметки."""
        cls.author = User.objects.create(username="testuser")
        cls.anon = User.objects.create(username="anonuser")
        cls.note = Note.objects.create(
            title="Заголовок", text="Текст", author=cls.author
        )

    def test_pages_availability(self):
        """Проверка домашней страницы и доступа."""
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.anon, HTTPStatus.OK),
        )
        urls = (
            ("notes:home", None),
            ("users:login", None),
            ("users:logout", None),
            ("users:signup", None),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name, args in urls:
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
            self.client.force_login(user)
            for name in (
                "notes:edit",
                "notes:delete",
                "notes:detail",
            ):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        """Проверка на редирект."""
        login_url = reverse("users:login")
        for name in (
            "notes:list",
            "notes:success",
            "notes:detail",
            "notes:edit",
            "notes:delete",
        ):
            with self.subTest(name=name):
                if name in ("notes:detail", "notes:edit", "notes:delete"):
                    url = reverse(name, args=(self.note.slug,))
                else:
                    url = reverse(name)
                redirect_url = f"{login_url}?next={url}"
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_pages_autentification(self):
        """Проверка доступа списка, добавления заметки."""
        users_statuses = ((self.author, HTTPStatus.OK),)
        urls = (
            ("notes:add", None),
            ("notes:success", None),
            ("notes:list", None),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name, args in urls:
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=args)
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, HTTPStatus.OK)
