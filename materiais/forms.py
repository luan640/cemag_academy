from django import forms
from .models import Pasta,Material,Visualizacao
from cadastros.models import Setor,Funcionario

import uuid
import os

class FuncionarioMatriculaChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return f"{obj.matricula} - {obj.nome}"

class AddPasta(forms.ModelForm):
    funcionarios = FuncionarioMatriculaChoiceField(
        queryset=Funcionario.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False  # Torna o campo não obrigatório

    )
    class Meta:
        model = Pasta
        fields = ('nome', 'descricao', 'area_trilha', 'setores', 'funcionarios')
        widgets = {
            'setores': forms.CheckboxSelectMultiple,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['setores'].queryset = Setor.objects.all()
        self.fields['setores'].required = False  # Torna o campo não obrigatório


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
            'pasta': forms.HiddenInput()  # Esconda o campo 'pasta'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['pasta'].required = False  # Certifique-se de que o campo não é obrigatório no formulário

    def save(self, commit=True):
        material = super().save(commit=False)
        
        # Renomear o arquivo de vídeo, se houver
        if self.cleaned_data.get('video'):
            material.video.name = self.rename_file(material.video, 'video')
        
        # Renomear o arquivo de documento, se houver
        if self.cleaned_data.get('arquivo'):
            material.arquivo.name = self.rename_file(material.arquivo, 'arquivo')
        
        # Renomear o arquivo de foto, se houver
        if self.cleaned_data.get('fotos'):
            material.fotos.name = self.rename_file(material.fotos, 'fotos')

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