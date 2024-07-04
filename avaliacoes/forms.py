from django import forms
from django.forms import modelformset_factory

from .models import Resposta

class CorrigirRespostaDissertativaForm(forms.ModelForm):
    class Meta:
        model = Resposta
        fields = ['nota', 'comentario', 'corrigida']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nota'].required = True
        self.fields['corrigida'].initial = True

    def save(self, commit=True):
        resposta = super().save(commit=False)
        resposta.corrigida = True  # Marca como corrigida ao salvar
        if commit:
            resposta.save()
        return resposta

CorrigirRespostaDissertativaFormSet = modelformset_factory(
    Resposta,
    form=CorrigirRespostaDissertativaForm,
    extra=0,  # Não permite adicionar novos formulários além dos já existentes
    can_delete=False,  # Não permite deletar formulários
)