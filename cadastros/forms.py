from django import forms
from .models import Funcionario, Area, Setor

class AddFuncionario(forms.ModelForm):
    class Meta:
        model = Funcionario
        fields = ('matricula', 'nome', 'setor')
    
    def __init__(self, *args, **kwargs):
        super(AddFuncionario, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

class AddSetor(forms.ModelForm):
    class Meta:
        model = Setor
        fields = ('area', 'nome')
    
    def __init__(self, *args, **kwargs):
        super(AddSetor, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

class AddArea(forms.ModelForm):
    class Meta:
        model = Area
        fields = ('nome',)
    
    def __init__(self, *args, **kwargs):
        super(AddArea, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
