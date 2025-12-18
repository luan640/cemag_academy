from django.http.response import HttpResponse as HttpResponse
from django.shortcuts import render,redirect,get_object_or_404
from .forms import CustomUserCreationForm, CustomUserFromFuncionarioCreationForm, CustomUserAdminEditForm
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
            form = CustomUserFromFuncionarioCreationForm(request.POST)
            if form.is_valid():
                funcionario = form.cleaned_data.get('funcionario')
                user = form.save(commit=False)
                user.matricula = funcionario.matricula
                nome_completo = (funcionario.nome or '').strip()
                partes = [p for p in nome_completo.split(' ') if p]
                if partes:
                    user.first_name = partes[0]
                    user.last_name = ' '.join(partes[1:])
                user.save()

                funcionario.user = user
                funcionario.save()

                return render(request, 'user/create_user.html', {
                    'form': CustomUserFromFuncionarioCreationForm(),
                    'success_message': 'Usuario associado ao funcionario com sucesso.'
                })
            else:
                messages.error(request, 'Formulario invalido. Verifique os campos e tente novamente.', extra_tags='matricula')

        form = CustomUserFromFuncionarioCreationForm()
        users = CustomUser.objects.all()
        edit_forms = {usuario.id: CustomUserAdminEditForm(instance=usuario) for usuario in users}
        return render(request, 'user/create_user.html', {
            'form': form,
            'users': users,
            'edit_forms': edit_forms,
        })
    else:
        return redirect('home')

@login_required
def edit_user(request, pk):
    if request.user.type != 'ADM':
        return redirect('home')

    usuario = get_object_or_404(CustomUser, pk=pk)
    if request.method != 'POST':
        return redirect('create-user')

    form = CustomUserAdminEditForm(request.POST, instance=usuario)
    if form.is_valid():
        form.save()
        messages.success(request, 'Usuario atualizado com sucesso.')
    else:
        messages.error(request, 'Formulario invalido. Verifique os campos e tente novamente.')
    return redirect('create-user')

@login_required
def toggle_user_active(request, pk):
    if request.user.type != 'ADM':
        return redirect('home')
    if request.method != 'POST':
        return redirect('create-user')

    usuario = get_object_or_404(CustomUser, pk=pk)
    if usuario.id == request.user.id:
        messages.error(request, 'Nao e possivel desabilitar o proprio usuario.')
        return redirect('create-user')

    usuario.is_active = not usuario.is_active
    usuario.save(update_fields=['is_active'])
    status = 'habilitado' if usuario.is_active else 'desabilitado'
    messages.success(request, f'Usuario {status} com sucesso.')
    return redirect('create-user')
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
        
        try:
            funcionario = Funcionario._base_manager.get(matricula=username)
            if funcionario.excluido:
                # Exibir mensagem de erro e redirecionar para a página de login
                messages.error(self.request, "Sua conta está desativada. Entre em contato com o administrador.", extra_tags='login')
                return redirect('login')
        except Funcionario.DoesNotExist:
            pass  # Caso o usuário não tenha um Funcionario associado, continuar normalmente

        return super().post(request, *args, **kwargs)
