from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    is_staff = forms.BooleanField(label='Is staff', required=False)

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('matricula', 'first_name', 'last_name', 'email', 'is_staff', 'password1', 'password2')

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('matricula', 'first_name', 'last_name', 'email')