from django.contrib.auth.models import User
from django.db import models

class Perfil(models.Model):
    USUARIO_TIPO = (
        ('Aluno', 'Aluno'),
        ('Professor', 'Professor'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    tipo_usuario = models.CharField(max_length=10, choices=USUARIO_TIPO)

    def __str__(self):
        return f"{self.user.username} - {self.tipo_usuario}"
