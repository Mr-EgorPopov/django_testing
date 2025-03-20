from http import HTTPStatus

from pytils.translit import slugify

from notes.models import Note
from notes.tests.class_note import CreateNote


class TestLogicNote(CreateNote):
    """Тест логики заметок."""

    def test_anonymous_user_cant_create_note(self):
        """Проверка на создание заметки анонимом."""
        self.notes_count_before = Note.objects.count()
        self.client.post(self.add_url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, self.notes_count_before)

    def test_user_can_create_note(self):
        """Проверка на создание заметки залогиненным пользователем."""
        Note.objects.all().delete()
        response = self.create_author_note()
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, self.reverse_success)
        self.assertEqual(Note.objects.count(), 1)
        created_note = Note.objects.get()
        self.assertEqual(created_note.title, self.form_data['title'])
        self.assertEqual(created_note.text, self.form_data['text'])
        self.assertEqual(created_note.author, self.author)

    def test_create_note_with_slug(self):
        """
        Проверка на создание заметки с одинаковым slug,
        а также проверка на автоматическое создание slug.
        """
        Note.objects.all().delete()
        self.form_data.pop("slug")
        response = self.create_author_note()
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, self.reverse_success)
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        expected_slug = slugify(self.form_data["title"])
        self.assertEqual(new_note.slug, expected_slug)

    def test_edit_note(self):
        """Проверка редактирования пользователем своей заметки."""
        response = self.edit_author_note()
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, self.reverse_success)
        note_after = Note.objects.get(id=self.note_author.id)
        self.assertEqual(note_after.title, self.updated_data["title"])
        self.assertEqual(note_after.text, self.updated_data["text"])
        self.assertEqual(note_after.author, self.note_author.author)

    def test_delete_note(self):
        """Проверка удаления пользователем своей заметки."""
        self.notes_count_before = Note.objects.count()
        self.delete_author_note()
        self.assertEqual(Note.objects.count(), self.notes_count_before - 1)

    def test_edit_strangers(self):
        """Проверка редактирования заметки другим пользователем."""
        response_not_author = self.edit_not_author_note()
        self.assertEqual(response_not_author.status_code, HTTPStatus.NOT_FOUND)
        note_after = Note.objects.get(id=self.note_author.id)
        self.assertEqual(note_after.title, self.note_author.title)
        self.assertEqual(note_after.text, self.note_author.text)
        self.assertEqual(note_after.author, self.note_author.author)

    def test_delete_strangers(self):
        """Проверка удаления заметки другим пользователем."""
        notes_count_before = Note.objects.count()
        self.delete_not_author_note()
        self.assertEqual(Note.objects.count(), notes_count_before)
