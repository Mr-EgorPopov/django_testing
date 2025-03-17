from http import HTTPStatus

from django.urls import reverse

from notes.tests.class_note import CreateNote


class TestNoteRoutes(CreateNote):
    """Тест доступа главной страницы."""

    def test_pages_availability(self):
        """Главная страница доступна анонимному пользователю."""
        for url in self.urls_home:
            with self.subTest(user=self.client, url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

        for url in self.urls_home:
            with self.subTest(user=self.client, url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_for_anonymous_client(self):
        """Проверка на редирект."""
        for name in self.url_list:
            with self.subTest(name=name):
                if name in self.url_edit:
                    url = reverse(name, args=(self.note_author.slug,))
                else:
                    url = reverse(name)
                redirect_url = f'{self.login}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_pages_autentification(self):
        """
        Аутентифицированному пользователю доступна страница
        со списком заметок notes/,
        страница успешного добавления заметки done/,
        страница добавления новой заметки add/.
        """
        users_statuses = ((self.author_client, HTTPStatus.OK),)
        for user, status in users_statuses:
            for url in self.url_add:
                with self.subTest(user=user, url=url):
                    response = self.author_client.get(url)
                    self.assertEqual(response.status_code, HTTPStatus.OK)
