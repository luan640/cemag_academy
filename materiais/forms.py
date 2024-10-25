from django import forms
from .models import Pasta,Material,Visualizacao
from cadastros.models import Setor,Funcionario
from django.forms.widgets import CheckboxSelectMultiple

import uuid
import os

class FuncionarioMatriculaChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return f"{obj.matricula} - {obj.nome}"

class AddPasta(forms.ModelForm):
    funcionarios = forms.ModelMultipleChoiceField(
        queryset=Funcionario.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'funcionario-checkbox'}),
        required=False  # Torna o campo não obrigatório
    )
    class Meta:
        model = Pasta
        fields = ('nome', 'descricao', 'area_trilha', 'setores', 'funcionarios')
        widgets = {
            'setores': forms.CheckboxSelectMultiple(attrs={'class': 'setor-checkbox'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 1, 'cols': 40})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Use select_related to avoid additional queries for user
        self.fields['funcionarios'].queryset = Funcionario.objects.select_related('user').prefetch_related('setor').all()
        self.fields['funcionarios'].label_from_instance = lambda obj: f"{obj.display_name()} {'(LÍD)' if obj.user and obj.user.type == 'LID' else ''}"

        for field_name, field in self.fields.items():
            if not isinstance(field.widget, forms.HiddenInput) and not isinstance(field.widget, forms.CheckboxSelectMultiple):
                field.widget.attrs.update({'class': 'form-control'})


    def save(self, commit=True):
        pasta = super().save(commit=False)
        if commit:
            pasta.save()
            self.save_m2m()  # Isso salva automaticamente as relações muitos-para-muitos
        return pasta

class AddMaterial(forms.ModelForm):
    class Meta:
        model = Material
        fields = ('nome', 'descricao', 'pasta', 'video', 'arquivo', 'fotos', 'video_youtube')
        widgets = {
            'pasta': forms.HiddenInput(),  # Esconda o campo 'pasta'
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 6, 'cols': 50})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['pasta'].required = False  # Certifique-se de que o campo não é obrigatório no formulário

        for field_name, field in self.fields.items():
            if not isinstance(field.widget, forms.HiddenInput):
                field.widget.attrs.update({'class': 'form-control'})

    def save(self, commit=True):
        material = super().save(commit=False)
        
        # Renomear o arquivo de vídeo, se houver e se for diferente do original
        if self.cleaned_data.get('video') and self.cleaned_data['video'] != material.video:
            material.video.name = self.rename_file(self.cleaned_data['video'], 'video')
        
        # Renomear o arquivo de documento, se houver e se for diferente do original
        if self.cleaned_data.get('arquivo') and self.cleaned_data['arquivo'] != material.arquivo:
            material.arquivo.name = self.rename_file(self.cleaned_data['arquivo'], 'arquivo')
        
        # Renomear o arquivo de foto, se houver e se for diferente do original
        if self.cleaned_data.get('fotos') and self.cleaned_data['fotos'] != material.fotos:
            material.fotos.name = self.rename_file(self.cleaned_data['fotos'], 'fotos')

        if commit:
            material.save()
        return material

    def rename_file(self, file, field_name):
        ext = file.name.split('.')[-1]
        new_filename = f"{field_name}_{uuid.uuid4()}.{ext}"
        return os.path.join(file.field.upload_to, new_filename)
    
class VisualizacaoForm(forms.ModelForm):
    class Meta:
        model = Visualizacao
        fields = ['funcionario', 'pasta', 'material']
        widgets = {
            'funcionario': forms.HiddenInput(),
            'pasta': forms.HiddenInput(),
            'material': forms.HiddenInput(),
        }