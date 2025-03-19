from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class CreateNote(TestCase):
    """Создание фикстур."""

    @classmethod
    def setUpTestData(cls):
        """Создание новостей."""
        cls.author = User.objects.create(username='author')
        cls.not_author = User.objects.create(username='user')
        cls.note_author = Note.objects.create(
            title='Заголовок', text='Текст', author=cls.author
        )
        cls.note_not_author = Note.objects.create(
            title='Заголовок_детект',
            text='Текст',
            author=cls.not_author
        )
        cls.edit_url_author = reverse(
            'notes:edit',
            args=[cls.note_author.slug]
        )
        cls.edit_url_not_author = reverse(
            'notes:edit',
            args=[cls.note_author.slug]
        )
        cls.delete_url_author = reverse(
            "notes:delete",
            args=[cls.note_author.slug]
        )
        cls.delete_url_not_author = reverse(
            "notes:delete",
            args=[cls.note_author.slug]
        )
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.not_author_client = Client()
        cls.not_author_client.force_login(cls.not_author)
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
        cls.edit_url = cls.edit_url_author
        cls.edit_url = reverse('notes:edit', args=(cls.note_author.slug,))
        cls.add_url = reverse('notes:add')
        cls.reverse_success = reverse("notes:success")
        cls.notes_list = reverse('notes:list')
        cls.home = reverse('notes:home')
        cls.detail = reverse('notes:detail', args=(cls.note_author.slug,))
        cls.login = reverse('users:login')
        cls.logaut = reverse('users:logout')
        cls.signup = reverse('users:signup')
        cls.urls_home = (
            cls.home,
            cls.login,
            cls.logaut,
            cls.signup,
        )
        cls.url_edit = (
            cls.edit_url_author,
            cls.delete_url_author,
            cls.detail,
        )
        cls.url_list = (
            cls.notes_list,
            cls.reverse_success,
            cls.detail,
            cls.edit_url_author,
            cls.delete_url_author,
        )
        cls.url_add = (
            cls.add_url,
            cls.reverse_success,
            cls.notes_list
        )

    def edit_author_note(self):
        """Редактирование заметки и возврат response."""
        return self.author_client.post(
            self.edit_url_author,
            data=self.updated_data
        )

    def delete_author_note(self):
        """Удаление заметки и возврат response."""
        return self.author_client.post(self.delete_url_author)

    def create_author_note(self):
        """Создание заметки и возврат response."""
        return self.author_client.post(self.add_url, data=self.form_data)

    def edit_not_author_note(self):
        """Редактирование заметки и возврат response."""
        return self.not_author_client.post(
            self.edit_url_not_author,
            data=self.updated_data
        )

    def delete_not_author_note(self):
        """Удаление заметки и возврат response."""
        return self.not_author_client.post(self.delete_url_not_author)

    def create_not_author_note(self):
        """Создание заметки и возврат response."""
        return self.not_author_client.post(self.add_url, data=self.form_data)
