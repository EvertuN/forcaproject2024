from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.models import Group
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import CadUsuarioForm


class UsuarioCreateView(CreateView):
    template_name = 'cadusuario.html'
    form_class = CadUsuarioForm
    success_url = reverse_lazy('loginuser')

    def form_valid(self, form):
        user = form.save()
        messages.success(self.request, f'Usuário cadastrado com sucesso!')
        login(self.request, user)
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request,
                       'Não foi possível cadastrar o usuário!!!')
        return super().form_invalid(form)

def cadastro(request):
    if request.method == 'POST':
        form = CadUsuarioForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = CadUsuarioForm()
    return render(request, 'usuarios/cadUsuario.html', {'form': form})
