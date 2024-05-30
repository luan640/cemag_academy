from django import forms
from .models import Pasta,Material
from cadastros.models import Setor,Funcionario

class AddPasta(forms.ModelForm):
    class Meta:
        model = Pasta
        fields = ('nome', 'descricao', 'setores', 'funcionarios')
        widgets = {
            'setores': forms.CheckboxSelectMultiple,
            'funcionarios': forms.CheckboxSelectMultiple,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['setores'].queryset = Setor.objects.all()
        self.fields['funcionarios'].queryset = Funcionario.objects.all()

    def save(self, commit=True):
        pasta = super().save(commit=False)
        if commit:
            pasta.save()
            self.save_m2m()
        return pasta


class AddMaterial(forms.ModelForm):
    class Meta:
        model = Material
        fields = ('nome','descricao','pasta','video','arquivo','fotos')
