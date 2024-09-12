from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.shortcuts import render, redirect
from .models import Tema, Palavra, Jogo
from .forms import TemaForm, PalavraForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import ListView, CreateView


class TemaCreateView(UserPassesTestMixin, CreateView):
    model = Tema
    form_class = TemaForm
    template_name = 'jogo/tema_form.html'

    def test_func(self):
        return self.request.user.is_staff

    def form_valid(self, form):
        form.instance.professor = self.request.user
        return super().form_valid(form)


class PalavraCreateView(UserPassesTestMixin, CreateView):
    model = Palavra
    form_class = PalavraForm
    template_name = 'jogo/palavra_form.html'

    def test_func(self):
        return self.request.user.is_staff


@login_required
def relatorio(request):
    jogos = Jogo.objects.filter(palavra__tema__professor=request.user)
    return render(request, 'jogo/relatorio.html', {'jogos': jogos})


# Views para o aluno
class TemaListView(ListView):
    model = Tema
    template_name = 'jogo/tema_list.html'


def jogar(request, tema_id):
    tema = get_object_or_404(Tema, id=tema_id)

    jogo_id = request.session.get('jogo_id')
    if jogo_id:
        jogo = get_object_or_404(Jogo, id=jogo_id)
        palavra = jogo.palavra.palavra.lower()
    else:
        palavra_obj = Palavra.objects.filter(tema=tema).order_by('?').first()
        jogo = Jogo.objects.create(palavra=palavra_obj)
        palavra = palavra_obj.palavra.lower()
        request.session['jogo_id'] = jogo.id

    letra_ja_usada = False  # Inicializa como falso

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

        if all([l in jogo.letras_corretas for l in palavra]):
            del request.session['jogo_id']
            return render(request, 'jogo/vitoria.html', {'palavra': jogo.palavra})

        if jogo.tentativas_restantes == 0:
            del request.session['jogo_id']
            return render(request, 'jogo/derrota.html', {'palavra': jogo.palavra})

    palavra_display = ''.join([l if l in jogo.letras_corretas else '_' for l in palavra])

    # Imagem correspondente ao número de erros
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
        'letra_ja_usada': letra_ja_usada,  # Adicionamos o contexto para avisar se a letra já foi usada
    }
    return render(request, 'jogo/jogo.html', contexto)

@login_required
def gerar_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="atividade.pdf"'

    c = canvas.Canvas(response, pagesize=letter)
    c.drawString(100, 750, "Relatório de Atividades")
    # Adicione mais conteúdo ao PDF
    c.showPage()
    c.save()

    return response
