from http import HTTPStatus

from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post, User


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_author = User.objects.create_user(username='user_author')
        cls.author = Client()
        cls.author.force_login(cls.user_author)
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовое описание группы',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user_author,
            group=cls.group
        )

    def setUp(self):
        cache.clear()
        self.guest_user = Client()


    def test_guest_user_exists_at_desired_location(self):
        """Проверяет доступность страниц для неавторизованного клиента."""
        urls = {
            '/': HTTPStatus.OK,
            f'/group/{PostURLTests.group.slug}/': HTTPStatus.OK,
            f'/profile/{PostURLTests.user_author}/': HTTPStatus.OK,
            f'/posts/{PostURLTests.post.id}/': HTTPStatus.OK,
            '/unexisting_page/': HTTPStatus.NOT_FOUND,
            f'/posts/{PostURLTests.post.id}/edit/': HTTPStatus.FOUND,
            '/create/': HTTPStatus.FOUND
        }

        for address, code in urls.items():
            with self.subTest(address=address):
                response = self.guest_user.get(address)
                self.assertEqual(response.status_code, code)

    def test_redirect_guest_user(self):
        """
        Проверяет редирект для неавторизованного клиента
        со страницы создания и редактирования поста.
        """
        login_url = reverse('users:login')
        page_name = {
            ('/create/'): (f'{login_url}?next=/create/'),
            (f'/posts/{PostURLTests.post.id}/edit/'):
                (f'{login_url}?next=/posts/{self.post.id}/edit/'),
            (f'/posts/{PostURLTests.post.id}/comment/'):
                (f'{login_url}?next=/posts/{self.post.id}/comment/')
        }
        for page, page_address in page_name.items():
            with self.subTest(page_address=page_address):
                response = self.guest_user.get(page)
                self.assertRedirects(response, page_address)


    def test_user_author_url_exists_at_desired_location(self):
        """Проверяет доступность страниц для автора."""
        urls = {
            '/': HTTPStatus.OK,
            f'/group/{PostURLTests.group.slug}/': HTTPStatus.OK,
            f'/profile/{PostURLTests.user_author}/': HTTPStatus.OK,
            f'/posts/{PostURLTests.post.id}/': HTTPStatus.OK,
            f'/posts/{PostURLTests.post.id}/edit/': HTTPStatus.OK,
            '/create/': HTTPStatus.OK
        }

        for address, code in urls.items():
            with self.subTest(address=address):
                response = PostURLTests.author.get(address)
                self.assertEqual(response.status_code, code)

    def test_user_authorized_url_exists_at_desired_location(self):
        """Проверяет доступность страниц для авторизованного клиента."""
        self.user_authorized = User.objects.create_user(
            username='user_authorized')
        self.authorized = Client()
        self.authorized.force_login(self.user_authorized)
        urls = {
            '/': HTTPStatus.OK,
            f'/group/{PostURLTests.group.slug}/': HTTPStatus.OK,
            f'/profile/{self.user_authorized}/': HTTPStatus.OK,
            f'/posts/{PostURLTests.post.id}/': HTTPStatus.OK,
            f'/posts/{PostURLTests.post.id}/edit/': HTTPStatus.FOUND,
            '/create/': HTTPStatus.OK
        }

        for address, code in urls.items():
            with self.subTest(address=address):
                response = self.authorized.get(address)
                self.assertEqual(response.status_code, code)

    def test_post_edit_redirect_user_authorized(self):
        """
        Проверяет редирект для авторизованного клиента
        со страницы редактирования поста.
        """
        self.user_authorized = User.objects.create_user(
            username='user_authorized')
        self.authorized = Client()
        self.authorized.force_login(self.user_authorized)
        response = self.authorized.get(f'/posts/{PostURLTests.post.id}/edit/')
        self.assertRedirects(response, (f'/posts/{self.post.id}/'))

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates = {
            '/': 'posts/index.html',
            f'/group/{PostURLTests.group.slug}/': 'posts/group_list.html',
            f'/profile/{PostURLTests.user_author}/': 'posts/profile.html',
            f'/posts/{PostURLTests.post.id}/': 'posts/post_detail.html',
            f'/posts/{PostURLTests.post.id}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html'
        }

        for address, template in templates.items():
            with self.subTest(address=address):
                response = PostURLTests.author.get(address)
                self.assertTemplateUsed(response, template)


class CoreURLTests(TestCase):
    def test_page_error(self):
        """Проверяет, что страница 404 отдаёт кастомный шаблон."""
        response = self.client.get('/nonexist-page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, 'core/404.html')
