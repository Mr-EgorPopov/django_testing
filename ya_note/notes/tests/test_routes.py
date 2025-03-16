from http import HTTPStatus

from django.urls import reverse

from notes.tests.class_note import CreateNote


class TestNoteRoutes(CreateNote):
    """Тест доступа главной страницы."""

    @classmethod
    def setUpTestData(cls):
        """Создание заметки."""
        super().setUpTestData()

    def test_pages_availability(self):
        """Проверка домашней страницы и доступа."""
        self.login_author()
        for url in self.urls_home:
            with self.subTest(user=self.author, url=url):
                response = self.auth_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

        for url in self.urls_home:
            with self.subTest(user=self.anon, url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_for_anonymous_client(self):
        """Проверка на редирект."""
        login_url = reverse('users:login')
        for name in self.url_list:
            with self.subTest(name=name):
                if name in self.url_edit:
                    url = reverse(name, args=(self.note_author.slug,))
                else:
                    url = reverse(name)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_pages_autentification(self):
        """Проверка доступа списка, добавления заметки."""
        users_statuses = ((self.author, HTTPStatus.OK),)
        for user, status in users_statuses:
            for url in self.url_add:
                with self.subTest(user=user, url=url):
                    self.user_login(user)
                    # У нас для разных тестов разные пользователи, я не понимаю
                    # как мы можем подготовить в setUpTestData(),
                    # я ведь уже подготовил
                    # и вызываю уже в самом тесте по мере необходимости
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, HTTPStatus.OK)
