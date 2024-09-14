from django.urls import path
from .views import relatorio

urlpatterns = [
    path('relatorio/', relatorio, name='relatorio'),
    # Outras URLs
]