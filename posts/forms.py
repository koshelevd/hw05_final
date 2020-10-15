"""Application 'posts' forms."""
from django.forms import ModelForm

from .models import Post, Comment


class PostForm(ModelForm):
    """
    New post form.

    Related to :model:'models.Post'.
    """

    class Meta:
        """
        Adds meta-information.

        Use :model:'models.Post' with fields 'text', 'group', 'image'.
        """

        model = Post
        fields = ('text', 'group', 'image',)
        help_texts = {
            'text': 'Содержание вашей записи (обязательное поле)',
            'group': 'Укажите сообщество (необязательно)',
            'image': 'Загрузите изображение (необязательно)',
        }


class CommentForm(ModelForm):
    """
    New comment form.

    Related to :model:'models.Comment'.
    """

    class Meta:
        """
        Adds meta-information.
        
        Use :model:'models.Comment' with field 'text'.
        """

        model = Comment
        fields = ('text',)
        help_texts = {
            'text': 'Комментарий (обязательное поле)',
        }
