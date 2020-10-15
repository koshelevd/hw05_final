"""Contains models to provide an Object-relational Mapping in 'posts' app."""
from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()


class Post(models.Model):
    """
    Stores a single post entry.

    Related to :model:'auth.User' and :model:'posts.Group'.
    """

    text = models.TextField(
        verbose_name='Содержание записи',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор',
    )
    group = models.ForeignKey(
        'Group',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='posts',
        verbose_name='Сообщество',
    )
    image = models.ImageField(
        upload_to='posts/',
        blank=True,
        null=True,
        verbose_name='Изображение',
    )

    def __str__(self):
        """Return post's info."""
        return (f'pk={self.pk} by {self.author}, {self.pub_date}, '
                f'group="{self.group}", text="{self.text[:50]}...", '
                f'image="{self.image}"')

    class Meta():
        """Adds meta-information."""

        ordering = ('-pub_date',)
        verbose_name_plural = 'Записи'
        verbose_name = 'Запись'


class Group(models.Model):
    """
    Stores a single group entry.

    Related to :model:'posts.Post'.
    """

    title = models.CharField(
        max_length=200,
        verbose_name='Название',
    )
    slug = models.SlugField(
        max_length=250,
        unique=True,
        verbose_name='ЧПУ',
    )
    description = models.TextField(
        verbose_name='Описание',
    )

    def __str__(self):
        """Return overrided title of the group."""
        return self.title

    class Meta():
        """Adds meta-information."""

        verbose_name_plural = 'Сообщества'
        verbose_name = 'Сообщество'


class Comment(models.Model):
    """
    Stores a single Comment entry.

    Related to :model:'auth.User' and :model:'posts.Post'.
    """

    post = models.ForeignKey(
        'Post',
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Запись',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор комментария',
    )
    text = models.TextField(
        verbose_name='Комментарий',
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата и время публикации',
    )

    def __str__(self):
        """Return comments's info."""
        return (f'Comment by {self.author}, {self.created}, '
                f'text="{self.text[:50]}..."')

    class Meta():
        """Adds meta-information."""

        ordering = ('-created',)
        verbose_name_plural = 'Комментарии'
        verbose_name = 'Комментарий'


class Follow(models.Model):
    """
    Stores followers and followings links.

    Related to :model:'auth.User'.
    """

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )

    def __str__(self):
        """Return followers's info."""
        return (f'Follow "{self.author}", '
                f'follower="{self.user}"')

    class Meta():
        """Adds meta-information."""

        unique_together = ('author', 'user',)
        verbose_name_plural = 'Подписчики'
        verbose_name = 'Подписчик'
