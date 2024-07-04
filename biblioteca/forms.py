from django import forms

from .models import Livro,Rating

import uuid
import os


class AddLivro(forms.ModelForm):

    IDIOMA_CHOICES = [
        ('Português', 'Português'),
        ('Inglês', 'Inglês'),
        ('Espanhol', 'Espanhol'),
        ('Francês', 'Francês'),
    ]

    idioma = forms.ChoiceField(choices=IDIOMA_CHOICES)
    
    class Meta:
        model = Livro
        fields = ['titulo', 'autor','ano','idioma','arquivo_pdf','capa']
        
    def save(self, commit=True):
        livro = super().save(commit=False)
        
        # Renomear o arquivo de vídeo, se houver
        if self.cleaned_data.get('arquivo_pdf'):
            livro.arquivo_pdf.name = self.rename_file(livro.arquivo_pdf, 'arquivo_pdf')
        
        # Renomear o arquivo de documento, se houver
        if self.cleaned_data.get('capa'):
            livro.capa.name = self.rename_file(livro.capa, 'capa')
        
        if commit:
            livro.save()
        return livro

    def rename_file(self, file, field_name):
        ext = file.name.split('.')[-1]
        new_filename = f"{field_name}_{uuid.uuid4()}.{ext}"
        return new_filename  # Apenas o novo nome do arquivo

class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['livro', 'score']
        widgets = {
            'livro': forms.HiddenInput(),
            'score': forms.RadioSelect(choices=[(i, i) for i in range(1, 6)])
        }
