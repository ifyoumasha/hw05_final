import tempfile
from http import HTTPStatus

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.forms import PostForm
from posts.models import Comment, Group, Post, User

NUMBER_OF_POSTS = 1


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
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

    def test_form_validity_post_create(self):
        """
        Проверяет, что при отправке валидной формы со страницы создания
        поста создаётся новая запись в базе данных.
        """
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
        form_data = {
            'text': 'Новая запись',
            'author': self.user_author,
            'group': self.group.id,
            'image': uploaded
        }
        posts_count = Post.objects.count()
        response = PostCreateFormTests.author.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        posts_count_after_request = Post.objects.count()
        self.assertEqual(
            posts_count_after_request, posts_count + NUMBER_OF_POSTS
        )
        last_post = Post.objects.last()
        self.assertEqual(last_post.text, form_data.get('text'))
        self.assertEqual(last_post.author, form_data.get('author'))
        self.assertEqual(last_post.group.id, form_data.get('group'))
        self.assertEqual(last_post.image, 'posts/small.gif')

    def test_form_validity_post_edit(self):
        """
        Проверяет, что при отправке валидной формы со страницы
        редактирования поста происходит изменение поста в базе данных.
        """
        post = Post.objects.create(
            text='Пост для редактирования',
            author=self.user_author,
            group=self.group
        )
        self.group_test = Group.objects.create(
            title='Группа для теста',
            slug='test-group',
            description='Описание группы'
        )
        form_data = {
            'text': 'Запись группы',
            'group': self.group_test.id
        }
        response = PostCreateFormTests.author.post(
            reverse('posts:post_edit', kwargs={'post_id': post.id}),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertNotEqual(post.text, form_data['text'])
        self.assertNotEqual(post.group, form_data['group'])

    def test_form_validity_post_detail(self):
        """
        Проверяет, что при отправке валидной формы со страницы
        поста комментарий появляется на странице.
        """
        comment_count = Comment.objects.count()
        post = Post.objects.create(
            text='Текст',
            author=self.user_author
        )
        form_data = {
            'text': 'Комментарий'
        }
        response = PostCreateFormTests.author.post(
            reverse('posts:add_comment', kwargs={'post_id': post.id}),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        comment_count_after_request = Comment.objects.count()
        self.assertEqual(
            comment_count_after_request, comment_count + NUMBER_OF_POSTS
        )
        last_post = Comment.objects.last()
        self.assertEqual(last_post.text, form_data.get('text'))


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.form = PostForm()

    def test_text_label(self):
        text_label = PostFormTests.form.fields['text'].label
        self.assertEquals(text_label, 'Текст поста')

    def test_text_help_text(self):
        text_help_text = PostFormTests.form.fields['text'].help_text
        self.assertEquals(text_help_text, 'Текст нового поста')

    def test_group_label(self):
        text_label = PostFormTests.form.fields['group'].label
        self.assertEquals(text_label, 'Группа')

    def test_group_help_text(self):
        text_help_text = PostFormTests.form.fields['group'].help_text
        self.assertEquals(
            text_help_text, 'Группа, к которой будет относиться пост'
        )
