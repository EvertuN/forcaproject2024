from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

class ProfessorRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return hasattr(self.request.user, 'perfil') and self.request.user.perfil.tipo_usuario == 'Professor'
