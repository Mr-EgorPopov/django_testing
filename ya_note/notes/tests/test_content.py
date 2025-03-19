from notes.forms import NoteForm
from notes.tests.class_note import CreateNote


class ContentTest(CreateNote):
    """Тестирование контента."""

    def test_has_form(self):
        """
        На страницы создания и редактирования
        заметки передаются формы.
        """
        urls = [
            (self.add_url),
            (self.edit_url),
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)

    def test_notes_list_include(self):
        """
        В список заметок одного пользователя
        не попадают заметки другого пользователя.
        """
        response = self.author_client.get(self.notes_list)
        notes = response.context['object_list']
        self.assertIn(self.note_author, notes)
        self.assertNotIn(self.note_not_author, notes)

    def test_note_in_context_object_list(self):
        """
        Отдельная заметка передаётся на страницу
        со списком заметок в списке object_list в словаре context.
        """
        response = self.author_client.get(self.notes_list)
        notes = response.context['object_list']
        self.assertIn(self.note_author, notes)
