from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView
from django.urls import path
from core import views
from core.views import relatorio_view
from usuarios.views import UsuarioCreateView


class CustomLogoutView(auth_views.LogoutView):
    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.IndexView.as_view(), name='home'),
    path('tema/add/', views.TemaCreateView.as_view(), name='adicionar_tema'),
    path('palavra/add/', views.PalavraCreateView.as_view(), name='adicionar_palavra'),
    path('temas/', views.TemaListView.as_view(), name='tema_list'),
    path('jogar/<int:tema_id>/', views.jogar, name='jogar'),
    path('relatorio/', views.gerar_relatorio_pdf, name='gerar_relatorio_pdf'),
    path('gerar_pdf/', views.gerar_pdf, name='gerar_pdf'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logoutuser'),
    path('accounts/login/', auth_views.LoginView.as_view(), name='loginuser'),
    path('cadastro/', UsuarioCreateView.as_view(), name='cadusuario'),
    path('relatorio/view/', relatorio_view, name='relatorio_view'),
]
