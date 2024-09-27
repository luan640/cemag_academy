from django.http.response import HttpResponse as HttpResponse
from django.shortcuts import render,redirect
from .forms import CustomUserCreationForm
from django.urls import reverse_lazy
from django.contrib.auth import logout,views as auth_views
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required

@login_required
def add_user(request):
    if request.user.type == 'ADM':
        if request.method == 'POST':
            form = CustomUserCreationForm(request.POST)
            if form.is_valid():
                user = form.save(commit=False)
                # user.is_staff = form.cleaned_data['is_staff']
                user.save()
                # Se o formulário for válido e o usuário for adicionado com sucesso, você pode redirecionar para a mesma página ou atualizar a página atual
                return render(request, 'user/create_user.html', {'form': CustomUserCreationForm(), 'success_message': 'User added successfully.'})
        else:
            form = CustomUserCreationForm()
        
        return render(request, 'user/create_user.html', {'form': form})
    else:
        return redirect('home')

def custom_404(request, exception):
    return render(request, '404.html', status=404)
    
class CustomLogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('login')  # Define a página de redirecionamento para a página de login

class CustomLoginView(LoginView):
    def dispatch(self, request, *args, **kwargs) -> HttpResponse:
        if request.user.is_authenticated:
            logout(request)
        return super().dispatch(request, *args, **kwargs)
