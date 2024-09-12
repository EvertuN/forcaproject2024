from django.contrib import admin

from core.models import Palavra, Tema


@admin.register(Tema)
class TemaAdmin(admin.ModelAdmin):
    list_display = ['nome']
    #prepopulated_fields = {'slug':('nome',)}


@admin.register(Palavra)
class PalavraAdmin(admin.ModelAdmin):
    list_display = ['palavra', 'tema', 'dica']
    list_filter = ['tema']
    #prepopulated_fields = {'slug':('palavra',)}
    #list_editable = ['preco', 'disponivel']