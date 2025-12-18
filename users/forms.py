from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from .models import CustomUser
from cadastros.models import Funcionario

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('matricula', 'first_name', 'last_name', 'email', 'type', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
        self.fields['email'].widget.attrs['placeholder'] = 'Digite o e-mail do usuário'
        self.fields['password1'].widget.attrs['class'] += ' another-class'


class CustomUserFromFuncionarioCreationForm(UserCreationForm):
    funcionario = forms.ModelChoiceField(
        queryset=Funcionario.objects.filter(user__isnull=True, excluido=False).select_related('user'),
        label='Funcionario',
        required=True
    )

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('funcionario', 'email', 'type', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super(CustomUserFromFuncionarioCreationForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
        self.fields['funcionario'].label_from_instance = lambda obj: f"{obj.matricula} - {obj.nome}"
        self.fields['email'].widget.attrs['placeholder'] = 'Digite o e-mail do usuario'

class CustomUserAdminEditForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'type')

    def __init__(self, *args, **kwargs):
        super(CustomUserAdminEditForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('matricula', 'first_name', 'last_name', 'email')

    def __init__(self, *args, **kwargs):
        super(CustomUserChangeForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['password'].widget.attrs.update({'class': 'form-control'})
