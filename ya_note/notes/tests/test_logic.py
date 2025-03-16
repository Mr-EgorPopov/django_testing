from http import HTTPStatus

from django.contrib.auth import get_user_model
from pytils.translit import slugify

from notes.models import Note
from notes.tests.class_note import CreateNote

User = get_user_model()


class TestLogicNote(CreateNote):
    """Тест Логики заметок."""

    @classmethod
    def setUpTestData(cls):
        """Настройка тестовых данных."""
        super().setUpTestData()

    def setUp(self):
        """Авторизация пользователя перед каждым тестом."""
        self.login_user()

    def create_note_response(self):
        """Создание заметки и возврат response."""
        return self.auth_client.post(self.add_url, data=self.form_data)

    def test_anonymous_user_cant_create_note(self):
        """Проверка на создание заметки анонимом."""
        self.notes_count_before = Note.objects.count()
        self.client.post(self.add_url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, self.notes_count_before)

    def test_user_can_create_note(self):
        """Проверка на создание заметки залогиненным юзером."""
        Note.objects.all().delete()
        self.notes_count_before = Note.objects.count()
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
        Note.objects.all().delete()
        self.form_data.pop("slug")
        self.notes_count_before = Note.objects.count()
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
        # Я не понимаю что от меня надо...
        # мы перстали чистить бд, теперь заметок куча,
        # нужна же привязка к определенной..
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
        self.notes_count_before = Note.objects.count()
        response = self.create_note_response()
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, self.reverse_success)
        note = Note.objects.get(slug="new-slug")
        self.delete_note_response(note)
        self.assertEqual(Note.objects.count(), self.notes_count_before)

    def test_edit_strangers(self):
        """Проверка редактирования заметки другим пользователем."""
        response = self.create_note_response()
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, self.reverse_success)
        note = Note.objects.get(slug="new-slug")
        self.auth_another()
        # И тут не понимаю, нам же надо залогинить другого пользователя
        # для того, чтобы проверить...
        response = self.edit_note_response(note)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_after = Note.objects.get(id=note.id)
        self.assertNotEqual(note_after.title, self.updated_data["title"])
        self.assertNotEqual(note_after.text, self.updated_data["text"])
        self.assertNotEqual(note_after.author, self.another)

    def test_delete_strangers(self):
        """Проверка удаления заметки другим пользователем."""
        response = self.create_note_response()
        notes_count_before = Note.objects.count()
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, self.reverse_success)
        note = Note.objects.get(slug="new-slug")
        self.auth_another()
        self.delete_note_response(note)
        self.assertEqual(Note.objects.count(), notes_count_before)
