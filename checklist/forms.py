from django import forms

from .models import Comment


class CommentForm(forms.ModelForm):
    """
    A class which specifies the form for the comment class

    Currently only body field is to be filled, other fields are auto-populated.
    """

    class Meta:
        model = Comment
        fields = ("body",)
