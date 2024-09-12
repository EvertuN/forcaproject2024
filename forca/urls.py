from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.TemaListView.as_view(), name='home'),
    path('tema/add/', views.TemaCreateView.as_view(), name='add-tema'),
    path('palavra/add/', views.PalavraCreateView.as_view(), name='add-palavra'),
    path('temas/', views.TemaListView.as_view(), name='temas'),
    path('jogar/<int:tema_id>/', views.jogar, name='jogar'),
    path('relatorio/', views.relatorio, name='relatorio'),
    path('gerar_pdf/', views.gerar_pdf, name='gerar_pdf'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logoutuser'),
    path('accounts/login/', auth_views.LoginView.as_view(), name='loginuser'),
]
