from django import forms
from .models import Tema, Palavra


class TemaForm(forms.ModelForm):
    class Meta:
        model = Tema
        fields = ['nome']


class PalavraForm(forms.ModelForm):
    class Meta:
        model = Palavra
        fields = ['palavra', 'tema', 'dica']
