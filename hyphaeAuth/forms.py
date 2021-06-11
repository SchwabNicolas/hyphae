from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.forms import ModelForm

from hyphaeAuth.models import HyphaeUser
from hyphaeAuth.validators import validate_user_email


class HyphaeUserCreationForm(UserCreationForm):
    email = forms.EmailField(validators=[validate_user_email])

    class Meta:
        model = HyphaeUser
        fields = ('email', 'first_name', 'last_name')


class HyphaeUserLoginForm(AuthenticationForm):
    username = forms.EmailField(label='Email')
