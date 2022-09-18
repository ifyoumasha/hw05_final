from django.test import TestCase
from posts.models import Group, Post, User

POST_LENGHT = 15


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост группы',
        )

    def test_models_have_correct_object_names(self):
        """Проверяет, что у моделей корректно работает __str__."""
        object_names = [
            (PostModelTest.post, self.post.text[:POST_LENGHT]),
            (PostModelTest.group, self.group.title)
        ]

        for name_model, expected_object_name in object_names:
            with self.subTest(name_model):
                self.assertEqual(str(name_model), expected_object_name)
