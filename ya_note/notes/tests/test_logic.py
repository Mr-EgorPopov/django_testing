from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from notes.models import Note
from pytils.translit import slugify

User = get_user_model()


class TestLogicNote(TestCase):
    """Тест Логики заметок."""

    @classmethod
    def setUpTestData(cls):
        """Настройка тестовых данных."""
        cls.url = reverse("notes:add")
        cls.user = User.objects.create(username="Залогиненный")
        cls.another = User.objects.create(username="Пользователь")
        cls.auth_client = Client()
        cls.form_data = {
            "title": "Новый заголовок",
            "text": "Новый текст",
            "slug": "new-slug",
        }
        cls.updated_data = {
            "title": "Обновленный заголовок",
            "text": "Обновленный текст",
            "slug": "new-slug",
        }
        cls.reverse_success = reverse("notes:success")

    def setUp(self):
        """Авторизация пользователя перед каждым тестом."""
        self.auth_client.force_login(self.user)
        self.notes_count_before = Note.objects.count()
        Note.objects.all().delete()

    def create_note_response(self):
        """Создание заметки и возврат response."""
        return self.auth_client.post(self.url, data=self.form_data)

    def edit_note_response(self, note):
        """Редактирование заметки и возврат response."""
        url = reverse("notes:edit", args=[note.slug])
        return self.auth_client.post(url, data=self.updated_data)

    def delete_note_response(self, note):
        """Удаление заметки и возврат response."""
        delete_url = reverse("notes:delete", args=[note.slug])
        return self.auth_client.post(delete_url)

    def auth_another(self):
        return self.auth_client.force_login(self.another)

    def test_anonymous_user_cant_create_note(self):
        """Проверка на создание заметки анонимом."""
        self.client.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, self.notes_count_before)

    def test_user_can_create_note(self):
        """Проверка на создание заметки залогиненным юзером."""
        response = self.create_note_response()
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, self.reverse_success)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, self.notes_count_before + 1)
        created_note = Note.objects.first()
        self.assertEqual(created_note.title, self.form_data['title'])
        self.assertEqual(created_note.text, self.form_data['text'])
        self.assertEqual(created_note.author, self.user)

    def test_create_note_with_slug(self):
        """
        Проверка на создание заметки с одинаковым slug,
        а также проверка на автоматическое создание slug.
        """
        self.form_data.pop("slug")
        response = self.create_note_response()
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, self.reverse_success)
        self.assertEqual(Note.objects.count(), self.notes_count_before + 1)
        new_note = Note.objects.get()
        expected_slug = slugify(self.form_data["title"])
        self.assertEqual(new_note.slug, expected_slug)

    def test_edit_note(self):
        """Проверка редактирования заметки."""
        response = self.create_note_response()
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, self.reverse_success)
        note = Note.objects.get(slug="new-slug")
        response = self.edit_note_response(note)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, self.reverse_success)
        note_after = Note.objects.get(id=note.id)
        self.assertEqual(note_after.title, self.updated_data["title"])
        self.assertEqual(note_after.text, self.updated_data["text"])
        self.assertEqual(note_after.author, self.user)

    def test_delete_note(self):
        """Проверка удаления заметки."""
        response = self.create_note_response()
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, self.reverse_success)
        note = Note.objects.get(slug="new-slug")
        self.delete_note_response(note)
        self.assertEqual(Note.objects.count(), 0)

    def test_edit_strangers(self):
        """Проверка редактирования заметки другим пользователем."""
        response = self.create_note_response()
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, self.reverse_success)
        note = Note.objects.get(slug="new-slug")
        self.auth_another()
        response = self.edit_note_response(note)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_after = Note.objects.get(id=note.id)
        self.assertNotEqual(note_after.title, self.updated_data["title"])
        self.assertNotEqual(note_after.text, self.updated_data["text"])
        self.assertNotEqual(note_after.author, self.another)

    def test_delete_strangers(self):
        """Проверка удаления заметки другим пользователем."""
        response = self.create_note_response()
        note_before = Note.objects.count()
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, self.reverse_success)
        note = Note.objects.get(slug="new-slug")
        self.auth_another()
        self.delete_note_response(note)
        self.assertEqual(Note.objects.count(), note_before)
