from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class CreateNote(TestCase):
    """Создание фикстур."""

    LIST_URL = reverse("notes:list")

    @classmethod
    def setUpTestData(cls):
        """Создание новостей."""
        cls.author = User.objects.create(username='author')
        cls.user = User.objects.create(username='user')
        cls.note_author = Note.objects.create(
            title='Заголовок', text='Текст', author=cls.author
        )
        cls.note_user = Note.objects.create(
            title='Заголовок_детект', text='Текст', author=cls.user
        )
        cls.add_url = reverse('notes:add')
        cls.edit_url = reverse('notes:edit', args=(cls.note_author.slug,))

    def setUp(self):
        """Авторизация пользователя перед каждым тестом."""
        self.client.force_login(self.author)

    def test_has_form(self):
        response_add = self.client.get(self.add_url)
        response_edit = self.client.get(self.edit_url)
        self.assertIn('form', response_add.context)
        self.assertIsInstance(response_add.context['form'], NoteForm)
        self.assertIn('form', response_edit.context)
        self.assertIsInstance(response_edit.context['form'], NoteForm)

    def test_notes_list_include(self):
        """
        В список одного пользователя
        не попадают заметки другого.
        """
        response = self.client.get(self.LIST_URL)
        object_list = response.context['object_list']
        self.assertIn(self.note_author, object_list)
        self.assertNotIn(self.note_user, object_list)

    def test_note_in_context_object_list(self):
        """
        Отдельная заметка передаётся на
        страницу со списком заметок.
        """
        response = self.client.get(self.LIST_URL)
        object_list = response.context['object_list']
        self.assertIn(self.note_author, object_list)
