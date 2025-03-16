from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

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
        cls.anon = User.objects.create(username='anonuser')
        cls.note_author = Note.objects.create(
            title='Заголовок', text='Текст', author=cls.author
        )
        cls.note_user = Note.objects.create(
            title='Заголовок_детект', text='Текст', author=cls.user
        )
        cls.add_url = reverse('notes:add')
        cls.edit_url = reverse('notes:edit', args=(cls.note_author.slug,))
        cls.client = cls.client_class()
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
        cls.urls_home = (
            reverse('notes:home', None),
            reverse('users:login', None),
            reverse('users:logout', None),
            reverse('users:signup', None),
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
            reverse('notes:add', None),
            reverse('notes:success', None),
            reverse('notes:list', None),
        )

    def login_author(self):
        """Логин автора для тестов."""
        self.client.force_login(self.author)

    def login_user(self):
        self.auth_client.force_login(self.user)

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

    def user_login(self, user):
        return self.client.force_login(user)
