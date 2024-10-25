from django.http.response import HttpResponse as HttpResponse
from django.shortcuts import render,redirect
from .forms import CustomUserCreationForm
from .models import CustomUser
from cadastros.models import Funcionario
from django.urls import reverse_lazy
from django.contrib.auth import logout,views as auth_views
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from .forms import CustomAuthenticationForm

@login_required
def add_user(request):
    if request.user.type == 'ADM':
        if request.method == 'POST':
            form = CustomUserCreationForm(request.POST)
            if form.is_valid():
                # Recuperar a matrícula do formulário
                matricula = form.cleaned_data.get('matricula')

                # Verificar se já existe um funcionário com essa matrícula
                try:
                    funcionario = Funcionario.objects.get(matricula=matricula)
                except Funcionario.DoesNotExist:
                    messages.error(request, f"Nenhum funcionário encontrado com a matrícula: {matricula}. Cadastre um Funcionário com essa mesma matrícula em 'Cadastros>>Funcionário'", extra_tags="matricula")
                    return render(request, 'user/create_user.html', {'form': form})

                # Criar e associar o CustomUser ao funcionário
                user = form.save(commit=False)
                user.save()

                # Associar o usuário ao funcionário encontrado
                funcionario.user = user
                funcionario.save()

                # Exibir uma mensagem de sucesso
                return render(request, 'user/create_user.html', {
                    'form': CustomUserCreationForm(),
                    'success_message': 'Usuário associado ao funcionário com sucesso.'
                })
            else:
                # Exibir erros do formulário para ajudar a identificar o problema
                messages.error(request, f"Formulário inválido. Verifique os campos e tente novamente. Matrículas já associadas a outros funcionários não poderão ser preenchidas novamente.", extra_tags="matricula")

        form = CustomUserCreationForm()
        users = CustomUser.objects.all()
        
        return render(request, 'user/create_user.html', {'form': form, 'users': users})
    else:
        return redirect('home')
def custom_404(request, exception):
    return render(request, '404.html', status=404)
    
class CustomLogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('login')  # Define a página de redirecionamento para a página de login
    
class CustomLoginView(LoginView):

    authentication_form = CustomAuthenticationForm  # Adicione esta linha
    def dispatch(self, request, *args, **kwargs) -> HttpResponse:
        if request.user.is_authenticated:
            logout(request)
        return super().dispatch(request, *args, **kwargs)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Matrícula ou senha incorretas.', extra_tags='login')
        return super().form_invalid(form)

    def post(self, request, *args, **kwargs):
        username = request.POST.get('username')
        if not username.isdigit():
            return self.form_invalid(self.get_form())
        return super().post(request, *args, **kwargs)