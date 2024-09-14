from django.db import models
from django.contrib.auth.models import User


class Tema(models.Model):
    nome = models.CharField(max_length=100)
    #professor = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'is_staff': True})

    class Meta:
        verbose_name = 'Tema'
        verbose_name_plural = 'Temas'
        ordering = ('nome',)

    def __str__(self):
        return self.nome


class Palavra(models.Model):
    palavra = models.CharField(max_length=100)
    tema = models.ForeignKey(Tema, on_delete=models.CASCADE)
    #texto = models.TextField(blank=True, null=True)
    dica = models.CharField(max_length=255, blank=True, null=True)
    criado = models.DateTimeField(auto_now_add=True)
    atualizado = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.palavra


class Jogador(models.Model):
    nome = models.CharField(max_length=100)
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='jogador')

    def __str__(self):
        return self.nome


class Jogo(models.Model):
    palavra = models.ForeignKey(Palavra, on_delete=models.CASCADE)
    tentativas_restantes = models.IntegerField(default=5)
    letras_corretas = models.CharField(max_length=100, blank=True)
    letras_erradas = models.CharField(max_length=100, blank=True)
    jogador = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='jogos')
    data_jogada = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.jogador.username if self.jogador else "Desconhecido"} - {self.palavra.palavra}'


