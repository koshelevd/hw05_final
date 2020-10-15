"""Test suite for 'post' application."""

from io import BytesIO
from os import path, remove
from uuid import uuid4

from django.core.cache import cache
from django.core.files.base import File
from django.test import Client, TestCase
from django.urls import reverse
from PIL import Image

from posts.models import Comment, Follow, Group, Post, User
from django.conf import settings


class TestPostApp(TestCase):
    """Tests for 'post' application."""

    ready_urls = {
        'INDEX': reverse('index'),
        'LOGIN': reverse('login'),
        'NEW_POST': reverse('new_post'),
        'FOLLOW_INDEX': reverse('follow_index'),
    }
    ready_urls['REDIRECT'] = (f'{ready_urls["LOGIN"]}?next='
                              f'{ready_urls["NEW_POST"]}')
    POST_TEXT = str(uuid4())
    IMAGE_NAME = str(uuid4())

    def setUp(self):
        """Set up test fixtures."""
        self.unauthorized_client = Client()
        self.authorized_client = Client()

        self.user = User.objects.create_user(username=str(uuid4()))
        self.authorized_client.force_login(self.user)

        self.group = self.group_create()
        self.image = self.get_image_file()

        self.ready_urls['PROFILE'] = reverse(
            'profile', args=(self.user.username,))
        self.ready_urls['FOLLOW'] = reverse(
            'profile_follow', args=(self.user.username,))
        self.ready_urls['UNFOLLOW'] = reverse(
            'profile_unfollow', args=(self.user.username,))

    def tearDown(self):
        """Delete temporary files after test."""
        img = f'{settings.MEDIA_ROOT}\\posts\\{self.IMAGE_NAME}'
        dat = 'test.dat'
        for file in (img, dat):
            if path.isfile(file):
                remove(file)

    def group_create(self):
        """Create a random group."""
        return Group.objects.create(
            title=str(uuid4()),
            slug=str(uuid4()),
            description=str(uuid4())
        )

    def get_image_file(self, ext='png', size=(25, 25), color=(256, 256, 256)):
        """Create a test image."""
        file_obj = BytesIO()
        image = Image.new("RGBA", size=size, color=color)
        image.save(file_obj, ext)
        file_obj.seek(0)
        name = self.IMAGE_NAME
        return File(file_obj, name=name)

    def post_create(self):
        """Create a test post record."""
        return Post.objects.create(
            author=self.user,
            text=self.POST_TEXT,
            group=self.group,
            image=self.image
        )

    def post_via_POST(self, client, file=None):
        """Publish new post using POST-request."""
        if file is None:
            image = self.image
        else:
            image = file
        data = {
            'text': self.POST_TEXT,
            'group': self.group.id,
            'image': image,
        }
        if client == self.authorized_client:
            data['author'] = self.user
        return client.post(self.ready_urls['NEW_POST'], data)

    def test_check_404_status(self):
        """Check 404 status of unknown page."""
        test_url = str(uuid4())
        response = self.unauthorized_client.get(test_url)
        with self.subTest('Wrong status for unknown page!'):
            self.assertEqual(response.status_code, 404)
        with self.subTest('Wrong template was used for 404 status!'):
            self.assertTemplateUsed(response, 'misc/404.html')

    def check_post_saved_correctly(self, post, data={}):
        """Check if passed 'post' corresponds to 'data'."""
        text_to_check = data.get('text', self.POST_TEXT)
        group_to_check = data.get('group', self.group.id)

        fields = (
            (post.author, self.user, 'Author does not match!'),
            (post.text, text_to_check, 'Text does not match!'),
            (post.group.id, group_to_check, 'Group does not match!'),
        )
        for value1, value2, message in fields:
            with self.subTest(message):
                self.assertEqual(value1, value2)

    def test_profile_page_exists_if_user_unauthorized(self):
        """Check status code of profile page for unuathorized user."""
        response = self.unauthorized_client.get(self.ready_urls['PROFILE'])
        self.assertEqual(response.status_code, 200)

    def test_profile_page_exists_if_user_authorized(self):
        """Check status code of profile page for authorized user."""
        response = self.authorized_client.get(self.ready_urls['PROFILE'])
        self.assertEqual(response.status_code, 200)

    def test_redirect_from_new_post_page_if_user_is_not_logged_in(self):
        """Check if /new/ page redirects user to login page."""
        response = self.unauthorized_client.get(self.ready_urls['NEW_POST'])
        self.assertRedirects(response, self.ready_urls['REDIRECT'])

    def test_logged_in_user_can_access_new_post_page(self):
        """Check status code for authorized user on /new/ page."""
        response = self.authorized_client.get(self.ready_urls['NEW_POST'])
        self.assertEqual(response.status_code, 200)

    def test_new_post_unauthorized(self):
        """Test if unauthorized user can't create new post."""
        posts_count_before = Post.objects.all().count()
        response = self.post_via_POST(self.unauthorized_client)
        posts_count_after = Post.objects.all().count()

        with self.subTest('No redirect in case of unauthorized posting!'):
            self.assertRedirects(response, self.ready_urls['REDIRECT'])

        with self.subTest('Unauthorized posting passed!'):
            self.assertEquals(posts_count_before, posts_count_after)

    def test_new_post_authorized(self):
        """
        Test if authorized user can create new post.

        ** Context **

        ''response''
            'HTTPResponse' on POST-request with new data.

        ''post''
            :model:'posts.Post' corresponding to posted data.

        """
        response = self.post_via_POST(self.authorized_client)
        post = Post.objects.get(pk=1)
        self.check_post_saved_correctly(post)
        with self.subTest('No redirect to main page!'):
            self.assertRedirects(response, self.ready_urls['INDEX'])

    def test_edit_post_authorized(self):
        """
        Test if authorized user can edit post.

        ** Context **

        'post'
            created object :model:'posts.Post'.

        'data_edited'
            new data to edit the 'post'.

        'response'
            'HTTPResponse' on POST-request with new data.

        'post_edited'
            :model:'posts.Post' corresponding to edited data.
        """
        post = self.post_create()
        data_edited = {
            'text': str(uuid4()),
            'group': self.group_create().id,
        }
        response = self.authorized_client.post(
            reverse('post_edit', args=(self.user.username, post.id)),
            data=data_edited
        )
        post_edited = Post.objects.get(pk=1)

        self.check_post_saved_correctly(post_edited, data_edited)
        with self.subTest('No redirect to post page!'):
            self.assertRedirects(
                response,
                reverse('post', args=(self.user.username, post.id))
            )

    def test_pages_contain_published_post(self):
        """Search specified pages using GET request."""
        cache.clear()
        post = self.post_create()
        pages = (
            self.ready_urls['INDEX'],
            self.ready_urls['PROFILE'],
            reverse('post', args=(self.user.username, post.id)),
            reverse('group_posts', args=(self.group.slug,))
        )
        for page in pages:
            page_response = self.authorized_client.get(page)
            with self.subTest('Post is not on "' + page + '"'):
                if 'paginator' in page_response.context:
                    self.assertIn(
                        post, page_response.context['paginator'].object_list)
                else:
                    self.assertEquals(post, page_response.context['post'])
            with self.subTest('Tag <img> not found: "' + page + '"'):
                self.assertContains(page_response, '<img')

    def test_upload_non_image_file(self):
        """Tests if we can not a post with non image file."""
        with open('test.dat', 'w+') as img:
            response = self.post_via_POST(self.authorized_client, file=img)
        post = Post.objects.get(pk=1)
        self.assertEquals(post.image, '')

    def test_index_page_is_cached(self):
        """Checks count of queries on index page."""
        cache.clear()
        with self.assertNumQueries(3):
            for _ in range(50):
                response = self.authorized_client.get(self.ready_urls['INDEX'])
                self.assertEqual(response.status_code, 200)

    def create_loggedin_user(self):
        """Create a user, a client, log in the user."""
        user = User.objects.create_user(username=str(uuid4()))
        client = Client()
        client.force_login(user)
        return user, client

    def test_user_can_follow(self):
        """Test if authentificated user can follow an author."""
        follower, follower_client = self.create_loggedin_user()
        response = follower_client.get(self.ready_urls['FOLLOW'])

        with self.subTest('No redirect after follow!'):
            self.assertRedirects(response, self.ready_urls['PROFILE'])

        followers_count = Follow.objects.all().count()
        with self.subTest('Following failed!'):
            self.assertEquals(followers_count, 1)

    def test_post_is_in_following_feed(self):
        """Check if post is in follower's feed."""
        follower, follower_client = self.create_loggedin_user()
        not_follower, not_follower_client = self.create_loggedin_user()
        response = follower_client.get(self.ready_urls['FOLLOW'])
        author_post = self.post_create()

        resp_follower = follower_client.get(
            self.ready_urls['FOLLOW_INDEX']).context['paginator'].object_list
        resp_not_follower = not_follower_client.get(
            self.ready_urls['FOLLOW_INDEX']).context['paginator'].object_list

        with self.subTest('Post is not in follower\'s feed!'):
            self.assertIn(author_post,
                          resp_follower)
        with self.subTest('Post is in non-follower\'s feed!'):
            self.assertNotIn(author_post,
                             resp_not_follower)

    def test_author_unfollow(self):
        """Test if authentificated user can unfollow an author."""
        follower, follower_client = self.create_loggedin_user()
        response = follower_client.get(self.ready_urls['FOLLOW'])
        response = follower_client.get(self.ready_urls['UNFOLLOW'])

        with self.subTest('No redirect after unfollow!'):
            self.assertRedirects(response, self.ready_urls['PROFILE'])
        followers_count = Follow.objects.all().count()
        with self.subTest('Unfollowing failed!'):
            self.assertEquals(followers_count, 0)


    def create_comment(self, client, data):
        """Create a test comment record."""
        return client.post(self.ready_urls['ADD_COMMENT'], data)

    def test_new_comment_authorized(self):
        """Test if authorized user can comment a post."""
        post = self.post_create()
        self.ready_urls['ADD_COMMENT'] = reverse(
            'add_comment', args=(self.user.username, post.id,))
        data = {
            'text': str(uuid4()),
            'post': post.id,
            'author': self.user,
        }

        comment_by_anauth_user = self.create_comment(
            self.unauthorized_client, data)
        comments_count = Comment.objects.all().count()
        with self.subTest('Unauthorized user can post a comment!'):
            self.assertEquals(comments_count, 0)

        comment_by_auth_user = self.create_comment(
            self.authorized_client, data)
        comments_count = Comment.objects.all().count()
        with self.subTest('Authorized user can not post a comment!'):
            self.assertEquals(comments_count, 1)
