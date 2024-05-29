from django import forms
from .models import Pasta,Material

class AddPasta(forms.ModelForm):
    class Meta:
        model = Pasta
        fields = ('nome', 'descricao')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['nome'].widget.attrs['readonly'] = True  # Torna o nome apenas leitura durante a edição


class AddMaterial(forms.ModelForm):
    class Meta:
        model = Material
        fields = ('nome','descricao','pasta','video','arquivo','fotos')
