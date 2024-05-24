from django import forms

from .models import Pasta

class AddPasta(forms.ModelForm):
    class Meta:
        model = Pasta
        fields = ('nome', 'descricao')