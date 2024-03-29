"""Application 'users' filters."""
from django import template


register = template.Library()


@register.filter 
def addclass(field, css):
    """Return class for input fields."""
    return field.as_widget(attrs={"class": css})
