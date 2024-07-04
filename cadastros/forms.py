from django import forms
from .models import Funcionario,Area,Setor

class AddFuncionario(forms.ModelForm):
    class Meta:
        model = Funcionario
        fields = ('matricula', 'nome', 'setor')

class AddSetor(forms.ModelForm):
    class Meta:
        model = Setor
        fields = ('area', 'nome')

class AddArea(forms.ModelForm):
    class Meta:
        model = Area
        fields = ('nome',)