from django.shortcuts import render,get_object_or_404,redirect
from django.contrib.auth.decorators import login_required,user_passes_test
from django.db.models import Q

from cadastros.models import Funcionario
from materiais.models import Pasta,Material,Visualizacao
from users.models import CustomUser
from materiais.utils import ProgressoTrilha

import numpy as np
    
@login_required
def painel_home(request):

    if request.user.type == 'ADM' or request.user.type == 'LID' or request.user.type == 'DIR':
        return redirect('painel_home_superuser')
    else:
        # funcionario = Funcionario.objects.filter(matricula=request.user.matricula)
        funcionario = Funcionario.objects.get(matricula=request.user.matricula)

        #Andamento de trilhas
        #pastas que o usuario tem acesso
        setor_do_usuario_object = Funcionario.objects.get(matricula=request.user.matricula)
        setor_do_usuario = setor_do_usuario_object.setor
        pastas = Pasta.objects.filter(Q(setores=setor_do_usuario) | Q(funcionarios__matricula=request.user.matricula)).distinct()

        
        progresso_trilha = ProgressoTrilha(funcionario, pastas)
        progresso_pasta = progresso_trilha.calcular_progresso_trilhas()

        progresso_trilhas = {
            'pastas': pastas,
            'progresso_pasta': progresso_pasta,
        }

        #Progresso geral
        progresso_geral=np.array(list(progresso_pasta.values())).mean()

        #Trilhas finalizadas
        trilhas_finalizadas=[]
        for pasta in pastas:
            if progresso_pasta[pasta.nome] == 100:
                trilhas_finalizadas.append(pasta.nome)

        trilhas_finalizadas=str(len(trilhas_finalizadas))+"/"+str(len(pastas))

        #Andamento por área
        media_progresso_area_trilha = progresso_trilha.calcular_media_progresso_area_trilha(progresso_pasta, pastas)

    return render(request,
                'home.html', {
                'funcionario':funcionario,
                'progresso_trilha':progresso_trilhas,
                'progresso_geral':progresso_geral,
                'trilhas_finalizadas':trilhas_finalizadas,
                'media_progresso_area_trilha':media_progresso_area_trilha,

                })

def painel_home_superuser(request):
    
    funcionario = Funcionario.objects.get(matricula=request.user.matricula)

    #Andamento de trilhas
    #pastas que o usuario tem acesso
    setor_do_usuario_object = Funcionario.objects.get(matricula=request.user.matricula)
    setor_do_usuario = setor_do_usuario_object.setor
    pastas = Pasta.objects.filter(Q(setores=setor_do_usuario) | Q(funcionarios__matricula=request.user.matricula)).distinct()

    print(pastas)

    progresso_trilha_individual_func = ProgressoTrilha(funcionario, pastas)
    progresso_pasta = progresso_trilha_individual_func.calcular_progresso_trilhas()

    progresso_trilha_individual_var = {
        'pastas': pastas,
        'progresso_pasta': progresso_pasta,
    }

    #Progresso geral
    progresso_geral_individual=np.array(list(progresso_pasta.values())).mean()

    #Trilhas finalizadas
    trilhas_finalizadas=[]
    for pasta in pastas:
        if progresso_pasta[pasta.nome] == 100:
            trilhas_finalizadas.append(pasta.nome)

    trilhas_finalizadas=str(len(trilhas_finalizadas))+"/"+str(len(pastas))

    #Andamento por área
    media_progresso_area_trilha_individual = progresso_trilha_individual_func.calcular_media_progresso_area_trilha(progresso_pasta, pastas)

    if request.user.type == 'ADM':

        funcionario_logado = Funcionario.objects.filter(matricula=request.user.matricula)

        #engajamento por funcionario
        funcionarios = Funcionario.objects.all()
        progresso_funcionarios = {}

        for funcionario in funcionarios:

            pastas = Pasta.objects.filter(Q(setores=funcionario.setor) | Q(funcionarios__matricula=funcionario.matricula))
            progresso_trilha = ProgressoTrilha(funcionario, pastas)
            progresso_pasta = progresso_trilha.calcular_progresso_trilhas()
            progresso_geral=np.array(list(progresso_pasta.values())).mean()
            progresso_funcionarios[funcionario] = {
                'progresso': progresso_geral,
                'matricula': funcionario.matricula
            }

        # último acesso por funcionário
        ultimos_acessos = CustomUser.objects.all().order_by('-last_login')

        #últimas trilhas criadas
        ultimas_trilhas = Pasta.objects.all().order_by('-created_at')
    
    else:

        funcionario_logado = Funcionario.objects.get(matricula=request.user.matricula)

        setor_funcionario_object = Funcionario.objects.get(matricula=request.user.matricula)
        setor_funcionario = setor_funcionario_object.setor

        #engajamento por funcionario
        funcionarios = Funcionario.objects.filter(setor=setor_funcionario)
        progresso_funcionarios = {}

        # Processo apenas do setor do lider
        funcionarios_ids = [funcionario.matricula for funcionario in funcionarios]  
        ultimos_acessos = CustomUser.objects.filter(matricula__in=funcionarios_ids).values('matricula','first_name', 'last_login').order_by('-last_login')

        for funcionario in funcionarios:

            pastas = Pasta.objects.filter(Q(setores=setor_funcionario) | Q(funcionarios__matricula=funcionario.matricula))

            progresso_trilha = ProgressoTrilha(funcionario, pastas)
            progresso_pasta = progresso_trilha.calcular_progresso_trilhas()
            progresso_geral=np.array(list(progresso_pasta.values())).mean()
            progresso_funcionarios[funcionario] = {
                'progresso': progresso_geral,
                'matricula': funcionario.matricula
            }
            
        #últimas trilhas criadas
        ultimas_trilhas = Pasta.objects.all().order_by('-created_at')
        
    if request.user.type == 'ADM':
        user_type = 'Administrador'
    else:
        user_type = 'Líder'

    return render(request,'home-superuser.html',{
            'user_type':user_type,
            'funcionario':funcionario_logado,
            'progresso_funcionarios':progresso_funcionarios,
            'ultimos_acessos':ultimos_acessos,
            'ultimas_trilhas':ultimas_trilhas,
            'media_progresso_area_trilha_individual': media_progresso_area_trilha_individual,
            'progresso_trilha':progresso_trilha,
            'progresso_geral_individual':progresso_geral_individual,
            'trilhas_finalizadas':trilhas_finalizadas,
            'progresso_trilha_individual':progresso_trilha_individual_var,

            })