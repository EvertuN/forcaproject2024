from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Perfil

class CadUsuarioForm(UserCreationForm):
    usable_password = None
    TIPO_USUARIO = (
        ('Aluno', 'Aluno'),
        ('Professor', 'Professor'),
    )
    tipo_usuario = forms.ChoiceField(choices=TIPO_USUARIO, required=True)

    class Meta:
        model = User
        fields = ['username', 'email',  'password1', 'password2', 'tipo_usuario']

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            perfil, created = Perfil.objects.get_or_create(user=user)
            perfil.tipo_usuario = self.cleaned_data['tipo_usuario']
            perfil.save()
        return user
