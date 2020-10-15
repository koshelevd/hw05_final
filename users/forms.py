"""Application 'users' forms."""
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model


User = get_user_model()


class CreationForm(UserCreationForm):
    """
    New user form.

    Related to :model:'User'.
    """

    class Meta(UserCreationForm.Meta):
        """
        Use :model:'User'.
        
        With fields 'first_name', 'last_name', 'username', 'email'.
        """

        model = User
        fields = ('first_name', 'last_name', 'username', 'email')
