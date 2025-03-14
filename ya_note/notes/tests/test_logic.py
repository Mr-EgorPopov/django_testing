from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from notes.models import Note
from pytils.translit import slugify

User = get_user_model()


class TestNoteCreation(TestCase):
    """Тест Логики."""

    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('notes:add')
        cls.user = User.objects.create(username='Залогиненный')
        cls.another = User.objects.create(username='Пользователь')
        cls.auth_client = Client()
        cls.form_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'new-slug'
        }
    
    def test_anonymous_user_cant_create_note(self):
        """
        Проверка на создание заметки анонимом.
        """
        self.client.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)
    
    def test_user_can_create_note(self):
        """
        Проверка на создание заметки залогиненным юзером.
        """
        self.auth_client.force_login(self.user)
        response = self.auth_client.post(self.url, data=self.form_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('notes:success'))
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_create_note(self):
        """
        Проверка на создание заметки с одинаковым slag,
        а так же проверка на автоматическое создание slag.
        """
        self.auth_client.force_login(self.user)
        url = reverse('notes:add')
        self.form_data.pop('slug')
        response = self.auth_client.post(url, data=self.form_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('notes:success'))
        assert Note.objects.count() == 1
        new_note = Note.objects.get()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)

    def test_edit_note(self):
        """
        Проверка редактирования заметки.
        """
        self.auth_client.force_login(self.user)
        url = reverse('notes:add')
        response = self.auth_client.post(url, data=self.form_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('notes:success'))
        note = Note.objects.get(slug='new-slug')
        updated_data = {
            'title': 'Обновленный заголовок',
            'text': 'Обновленный текст',
            'slug': 'new-slug'
        }
        url = reverse('notes:edit', args=[note.slug])
        response = self.auth_client.post(url, data=updated_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('notes:success'))
        note.refresh_from_db()
        self.assertEqual(note.title, updated_data['title'])
        self.assertEqual(note.text, updated_data['text'])

    def test_delete_note(self):
        """
        Проверка удаления заметки.
        """
        self.auth_client.force_login(self.user)
        url = reverse('notes:add')
        response = self.auth_client.post(url, data=self.form_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('notes:success'))
        assert Note.objects.count() == 1
        note = Note.objects.get(slug='new-slug')
        url = reverse('notes:delete', args=[note.slug])
        response = self.auth_client.post(url)
        assert Note.objects.count() == 0

    def test_edit_strangers(self):
        """
        Проверка редактирования заметки другим пользователем.
        """
        self.auth_client.force_login(self.user)
        url = reverse('notes:add')
        response = self.auth_client.post(url, data=self.form_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('notes:success'))
        note = Note.objects.get(slug='new-slug')
        self.auth_client.force_login(self.another)
        updated_data = {
            'title': 'Попытка изменить заголовок',
            'text': 'Попытка изменить текст',
            'slug': note.slug
        }
        url = reverse('notes:edit', args=[note.slug])
        response = self.auth_client.post(url, data=updated_data)
        self.assertEqual(response.status_code, 404)
        note.refresh_from_db()
        self.assertNotEqual(note.title, updated_data['title'])
        self.assertNotEqual(note.text, updated_data['text'])

    def test_delete_strangers(self):
        """
        Проверка удаления заметки другим пользователем.
        """
        self.auth_client.force_login(self.user)
        url = reverse('notes:add')
        response = self.auth_client.post(url, data=self.form_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('notes:success'))
        assert Note.objects.count() == 1
        note = Note.objects.get(slug='new-slug')
        url = reverse('notes:delete', args=[note.slug])
        self.auth_client.force_login(self.another)
        response = self.auth_client.post(url)
        assert Note.objects.count() == 1
