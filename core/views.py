from datetime import datetime
from django.contrib import messages
from django.contrib.auth import logout
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.utils.timezone import now
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.shortcuts import render, redirect
from .mixins import ProfessorRequiredMixin
from .models import Tema, Palavra, Jogo
from .forms import TemaForm, PalavraForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.views.generic import ListView, CreateView, TemplateView

from .utils import gerar_relatorio


class TemaCreateView(ProfessorRequiredMixin, CreateView):
    model = Tema
    fields = ['nome']
    template_name = 'jogo/tema_form.html'
    success_url = reverse_lazy('tema_list')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.perfil.tipo_usuario != 'Professor':
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class PalavraCreateView(ProfessorRequiredMixin, CreateView):
    model = Palavra
    fields = ['palavra', 'tema', 'dica']
    template_name = 'jogo/palavra_form.html'
    success_url = reverse_lazy('tema_list')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.perfil.tipo_usuario != 'Professor':
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


@login_required
def relatorio(request):
    tema_id = request.GET.get('tema_id')

    if not tema_id or not tema_id.isdigit():
        return HttpResponseBadRequest("ID de tema inválido.")

    tema = get_object_or_404(Tema, id=int(tema_id))

    relatorio_dados = gerar_relatorio(tema)

    return render(request, 'jogo/relatorio.html', {'relatorio_dados': relatorio_dados})


# Views para o aluno
class TemaListView(ListView):
    model = Tema
    template_name = 'jogo/tema_list.html'
    context_object_name = 'temas'



class IndexView(TemplateView):
    template_name = 'index.html'


def jogar(request, tema_id):
    tema = get_object_or_404(Tema, id=tema_id)

    # Resetar o jogo se um novo tema for escolhido
    if 'tema_id' in request.session and request.session['tema_id'] != tema_id:
        if 'jogo_id' in request.session:
            del request.session['jogo_id']  # Remove o jogo anterior

    request.session['tema_id'] = tema_id  # Armazena o tema atual

    jogo_id = request.session.get('jogo_id')
    if jogo_id:
        jogo = get_object_or_404(Jogo, id=jogo_id)
        palavra = jogo.palavra.palavra.lower()
    else:
        palavra_obj = Palavra.objects.filter(tema=tema).order_by('?').first()
        jogo = Jogo.objects.create(palavra=palavra_obj)
        palavra = palavra_obj.palavra.lower()
        request.session['jogo_id'] = jogo.id

    letra_ja_usada = False

    if request.method == 'POST':
        letra = request.POST.get('letra').lower()

        if letra in jogo.letras_corretas or letra in jogo.letras_erradas:
            letra_ja_usada = True
            messages.warning(request, "Essa letra já foi usada!")
        elif letra in palavra:
            jogo.letras_corretas += letra
        else:
            jogo.letras_erradas += letra
            jogo.tentativas_restantes -= 1

        jogo.save()

        if all([l in jogo.letras_corretas or l == ' ' for l in palavra]):
            del request.session['jogo_id']
            return render(request, 'jogo/vitoria.html', {'palavra': jogo.palavra})

        if jogo.tentativas_restantes == 0:
            del request.session['jogo_id']
            return render(request, 'jogo/derrota.html', {'palavra': jogo.palavra})

    palavra_display = ''.join([l if l in jogo.letras_corretas or l == ' ' else '_' for l in palavra])

    imagens_erros = {
        5: 'forca0.jpg',
        4: 'forca0.jpg',
        3: 'forca1.jpg',
        2: 'forca2.jpg',
        1: 'forca3.jpg',
        0: 'forca4.jpg',
    }
    imagem_atual = imagens_erros[jogo.tentativas_restantes]

    contexto = {
        'tema': tema,
        'palavra_display': palavra_display,
        'tentativas_restantes': jogo.tentativas_restantes,
        'letras_erradas': jogo.letras_erradas,
        'imagem_forca': imagem_atual,
        'letra_ja_usada': letra_ja_usada,
    }
    return render(request, 'jogo/jogo.html', contexto)

@login_required
def gerar_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="atividade.pdf"'

    c = canvas.Canvas(response, pagesize=letter)
    c.drawString(100, 750, "Relatório de Atividades")
    c.showPage()
    c.save()

    return response

def is_professor(user):
    return hasattr(user, 'perfil') and user.perfil.tipo_usuario == 'Professor'

@login_required
@user_passes_test(lambda u: u.perfil.tipo_usuario == 'Professor')
def gerar_relatorio_pdf(request):
    tema_id = request.GET.get('tema_id')
    temas = Tema.objects.all()  # Pode filtrar se necessário

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="relatorio_completo.pdf"'

    p = canvas.Canvas(response)

    p.drawString(100, 800, f"Relatório Completo - {now()}")

    y = 750
    for tema in temas:
        p.drawString(100, y, f"Tema: {tema.nome}")
        jogos_tema = Jogo.objects.filter(palavra__tema=tema)
        for jogo in jogos_tema:
            jogador_nome = jogo.jogador.username if jogo.jogador else 'Desconhecido'
            p.drawString(100, y - 20, f"Jogo: {jogo.palavra.palavra} | Jogador: {jogador_nome}")
            y -= 20

        y -= 40

        if y < 50:
            p.showPage()
            y = 750

    p.showPage()
    p.save()
    return response

def professor_required(user):
    if user.is_authenticated and hasattr(user, 'perfil') and user.perfil.tipo_usuario == "Professor":
        return True
    raise PermissionDenied

@login_required
@user_passes_test(professor_required)
def adicionar_tema(request):
    if request.method == 'POST':
        form = TemaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = TemaForm()
    return render(request, 'tema_form.html', {'form': form})

@login_required
@user_passes_test(professor_required)
def adicionar_palavra(request):
    if request.method == 'POST':
        form = PalavraForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = PalavraForm()
    return render(request, 'palavra_form.html', {'form': form})


def relatorio_view(request):
    temas = Tema.objects.all()
    relatorios = []

    for tema in temas:
        jogos = Jogo.objects.filter(palavra__tema=tema).select_related('jogador', 'palavra')
        relatorios.append({
            'tema': tema.nome,
            'jogos': [{
                'jogador': jogo.jogador.username if jogo.jogador and jogo.jogador.username else 'Desconhecido',
                'palavra': jogo.palavra.palavra
            } for jogo in jogos]
        })

    return render(request, 'jogo/relatorio.html', {'relatorios': relatorios})


