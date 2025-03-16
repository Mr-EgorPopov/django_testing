

from notes.forms import NoteForm
from notes.tests.class_note import CreateNote


class Fixture(CreateNote):
    """Создание фикстур."""

    @classmethod
    def setUpTestData(cls):
        """Создание новостей."""
        super().setUpTestData()

    def setUp(self):
        """Авторизация пользователя перед каждым тестом."""
        self.login_author()

    def test_has_form(self):
        urls = [
            (self.add_url),
            (self.edit_url),
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)

    def test_notes_list_include(self):
        """
        В список одного пользователя
        не попадают заметки другого.
        """
        response = self.client.get(self.LIST_URL)
        notes = response.context['object_list']
        self.assertIn(self.note_author, notes)
        self.assertNotIn(self.note_user, notes)

    def test_note_in_context_object_list(self):
        """
        Отдельная заметка передаётся на
        страницу со списком заметок.
        """
        response = self.client.get(self.LIST_URL)
        object_list = response.context['object_list']
        self.assertIn(self.note_author, object_list)
