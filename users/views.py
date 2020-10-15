"""View functions of the 'users' app."""
from django.views.generic import CreateView
from django.urls import reverse_lazy
from .forms import CreationForm


class SignUp(CreateView):
    """Display sign up form for new user."""

    form_class = CreationForm
    success_url = reverse_lazy("login")
    template_name = "signup.html"
