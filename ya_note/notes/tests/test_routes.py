from http import HTTPStatus

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
        for url in self.url_list:
            with self.subTest(url=url):
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
        for url in self.url_add:
            with self.subTest(user=self.author_client, url=url):
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
