from django import forms
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Follow, Group, Post, User

NUMBER_OF_POSTS_TEST = 13
FIRST_PAGE_POSTS = 10
SECOND_PAGE_POSTS = 3
NUMBER_OF_FOLLOW = 1


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
        cls.group_test = Group.objects.create(
            title='Group',
            slug='another-slug',
            description='Group for test'
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user_author,
            group=cls.group,
            image=uploaded
        )

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        cache.clear()
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': self.group.slug}):
                'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': self.user_author}):
                'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}):
                'posts/post_detail.html',
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}):
                'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html'
        }

        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = PostURLTests.author.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        cache.clear()
        response = PostURLTests.author.get(reverse('posts:index'))
        page_obj = response.context.get('page_obj')
        self.assertIsNotNone(page_obj)
        self.assertGreater(len(page_obj), 0)
        first_object = response.context['page_obj'][0]
        self.assertIsNotNone(first_object)
        self.assertEqual(first_object.text, self.post.text)
        self.assertEqual(first_object.author, self.user_author)
        self.assertEqual(first_object.group, self.group)
        self.assertEqual(first_object.image, self.post.image)

    def test_group_posts_page_show_correct_context(self):
        """Шаблон group_posts сформирован с правильным контекстом."""
        response = PostURLTests.author.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            )
        )
        group = response.context.get('group')
        self.assertIsNotNone(group)
        page_obj = response.context.get('page_obj')
        self.assertIsNotNone(page_obj)
        self.assertGreater(len(page_obj), 0)
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.text, self.post.text)
        self.assertEqual(first_object.author, self.user_author)
        self.assertEqual(first_object.group, self.group)
        self.assertEqual(first_object.image, self.post.image)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = PostURLTests.author.get(
            reverse(
                'posts:profile',
                kwargs={'username': self.user_author}
            )
        )
        author = response.context.get('author')
        self.assertIsNotNone(author)
        page_obj = response.context.get('page_obj')
        self.assertIsNotNone(page_obj)
        self.assertGreater(len(page_obj), 0)
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.text, self.post.text)
        self.assertEqual(first_object.author, self.user_author)
        self.assertEqual(first_object.group, self.group)
        self.assertEqual(first_object.image, self.post.image)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = PostURLTests.author.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}
            )
        )
        post = response.context.get('post')
        self.assertIsNotNone(post)
        first_object = response.context['post']
        self.assertEqual(first_object.text, self.post.text)
        self.assertEqual(first_object.author, self.user_author)
        self.assertEqual(first_object.group, self.group)
        self.assertEqual(first_object.image, self.post.image)

    def test_post_edit_page_show_correct_context(self):
        """
        Шаблон post_edit и post_create сформированы
        с правильным контекстом.
        """
        page_name = [
            (reverse('posts:post_edit', kwargs={'post_id': self.post.id})),
            (reverse('posts:post_create'))
        ]
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for page in page_name:
            response = PostURLTests.author.get(page)
            for value, expected in form_fields.items():
                with self.subTest(value=value):
                    fields = response.context.get('form').fields.get(value)
                    self.assertIsInstance(fields, expected)

    def test_post_creation(self):
        """
        Проверяет, что если при создании поста указать группу, то пост
        появляется на соответствующих страницах.
        """
        page_group = PostURLTests.author.get(
            reverse('posts:group_list', kwargs={'slug': self.group_test.slug})
        )
        page_obj = page_group.context['page_obj']
        self.assertNotIn(PostURLTests.post, page_obj, None)

    def test_cache_index(self):
        """Проверяет кеширование главной страницы."""
        cache.clear()
        post = Post.objects.create(
            text='Пост',
            author=self.user_author,
            group=self.group
        )
        content_page_post = PostURLTests.author.get(
            reverse('posts:index')).content
        post.delete()
        content_page = PostURLTests.author.get(
            reverse('posts:index')).content
        self.assertEqual(content_page_post, content_page)
        cache.clear()
        page_after_cache_clear = PostURLTests.author.get(
            reverse('posts:index')).content
        self.assertNotEqual(content_page_post, page_after_cache_clear)


class FollowTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cache.clear()
        cls.user_author = User.objects.create_user(username='user_author')
        cls.author = Client()
        cls.author.force_login(cls.user_author)
        cls.user_authorized = User.objects.create_user(
            username='user_authorized')
        cls.authorized = Client()
        cls.authorized.force_login(cls.user_authorized)
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

    def test_authorized_user_follow_other_users(self):
        """
        Авторизованный пользователь может подписываться
        на других пользователей.
        """
        cache.clear()
        follow_count = Follow.objects.count()
        self.authorized.post(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.user_author}
            )
        )
        follow_count_after_follow = Follow.objects.count()
        self.assertEqual(
            follow_count_after_follow, follow_count + NUMBER_OF_FOLLOW
        )
        self.assertTrue(Follow.objects.filter(  
                        user=self.user_authorized, 
                        author=self.user_author
                        ).exists()) 

    def test_authorized_user_unfollow_other_users(self):
        """
        Авторизованный пользователь может отписаться
        от других пользователей.
        """
        cache.clear()
        Follow.objects.create(
            user=self.user_authorized,
            author=self.user_author
        )
        follow_count_after_follow = Follow.objects.count()
        self.authorized.post(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': self.user_author}
            )
        )
        follow_count_after_unfollow = Follow.objects.count()
        self.assertEqual(
            follow_count_after_follow - NUMBER_OF_FOLLOW,
            follow_count_after_unfollow
        )
        self.assertFalse(Follow.objects.filter(  
                        user=self.user_authorized, 
                        author=self.user_author
                        ).exists()) 


    def test_new_post_user_in_follow(self):
        """
        Новая запись пользователя появляется в ленте тех,
        кто на него подписан.
        """
        post = Post.objects.create(
            text='Пост',
            author=self.user_author,
            group=self.group
        )
        Follow.objects.create(
            user=self.user_authorized,
            author=self.user_author
        )
        response = self.authorized.get(
            reverse(
                'posts:follow_index'
            )
        )
        page_obj = response.context['page_obj'].object_list
        self.assertIn(post, page_obj)

    def test_new_post_user_in_unfollow(self):
        """
        Новая запись пользователя не появляется в ленте тех,
        кто на него не подписан.
        """
        post = Post.objects.create(
            text='Пост',
            author=self.user_author,
            group=self.group
        )
        response = self.authorized.get(
            reverse(
                'posts:follow_index'
            )
        )
        page_obj = response.context['page_obj'].object_list
        self.assertNotIn(post, page_obj)


class PaginatorViewsTest(TestCase):
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
        Post.objects.bulk_create(
            Post(text=f'Тестовый текст №{post}',
                author=cls.user_author,
                group=cls.group)for post in range(NUMBER_OF_POSTS_TEST))

    def test_first_page_contains_ten_records(self):
        cache.clear()
        paginator_pages = {
            reverse('posts:index'): FIRST_PAGE_POSTS,
            reverse('posts:index') + '?page=2': SECOND_PAGE_POSTS,
            reverse(
                'posts:group_list', kwargs={'slug': self.group.slug}
            ): FIRST_PAGE_POSTS,
            reverse(
                'posts:group_list', kwargs={'slug': self.group.slug}
            ) + '?page=2': SECOND_PAGE_POSTS,
            reverse(
                'posts:profile', kwargs={'username': self.user_author}
            ): FIRST_PAGE_POSTS,
            reverse(
                'posts:profile', kwargs={'username': self.user_author}
            ) + '?page=2': SECOND_PAGE_POSTS
        }
        for reverse_name, number_of_posts_in_page in paginator_pages.items():
            with self.subTest(reverse_name=reverse_name):
                response = PaginatorViewsTest.author.get(reverse_name)
                self.assertEqual(
                    len(response.context['page_obj']), number_of_posts_in_page
                )
