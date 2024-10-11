from django.shortcuts import render,get_object_or_404,redirect
from django.contrib.auth.decorators import login_required,user_passes_test
from django.db.models import Q
from django.http import JsonResponse

from cadastros.models import Funcionario
from materiais.models import Pasta,Material,Visualizacao,Setor
from users.models import CustomUser
from materiais.utils import ProgressoTrilha

import time
import numpy as np
import json

# def assiduidade_por_setor_api(request):
#     setores = Setor.objects.all()
#     assiduidade_por_setor = {}

#     for setor in setores:
#         # Funcionários do setor
#         funcionarios_setor = Funcionario.objects.filter(setor=setor)
#         total_funcionarios = funcionarios_setor.count()

#         if total_funcionarios > 0:
#             # Quantidade total de materiais disponíveis para o setor
#             total_materiais_setor = Material.objects.filter(pasta__setores=setor).count()

#             if total_materiais_setor > 0:
#                 # Quantidade total de visualizações por funcionários do setor
#                 total_visualizacoes = Visualizacao.objects.filter(funcionario__in=funcionarios_setor, pasta__setores=setor).count()
                
#                 # Calculando a proporção de visualizações
#                 proporcao_visualizacao = (total_visualizacoes / (total_funcionarios * total_materiais_setor)) * 100
#                 assiduidade_por_setor[setor.nome] = f"{proporcao_visualizacao:.2f}%"
#             else:
#                 assiduidade_por_setor[setor.nome] = "Nenhum material disponível"
#         else:
#             assiduidade_por_setor[setor.nome] = "Nenhum funcionário no setor"

#     return JsonResponse(assiduidade_por_setor)

# def trilhas_por_setor_api(request):
#     if request.method == 'POST':
#         try:
#             # Ler o corpo da solicitação JSON
#             data = json.loads(request.body)
#             setor_nome = data.get('setor')  # Nome do setor enviado no corpo da solicitação
            
#             # Verifica se o setor foi fornecido
#             if not setor_nome:
#                 return JsonResponse({'error': 'Setor não fornecido'}, status=400)

#             # Tenta encontrar o setor
#             setor = get_object_or_404(Setor, nome=setor_nome)

#             # Conta as pastas associadas ao setor específico
#             pastas_setor = Pasta.objects.filter(setores=setor)
#             trilhas_por_setor = {setor.nome: pastas_setor.count()}
            
#             return JsonResponse(trilhas_por_setor)

#         except json.JSONDecodeError:
#             return JsonResponse({'error': 'Formato JSON inválido'}, status=400)
#     else:
#         # Para GET ou outras requisições, retorna todas as trilhas
#         setores = Setor.objects.all()
#         trilhas_por_setor = {}

#         for setor in setores:
#             pastas_setor = Pasta.objects.filter(setores=setor)
#             trilhas_por_setor[setor.nome] = pastas_setor.count()

#         return JsonResponse(trilhas_por_setor)
    
@login_required
def painel_home(request):

    if request.user.type == 'ADM' or request.user.type == 'LID' or request.user.type == 'DIR':
        return redirect('painel_home_superuser')
    else:
        # funcionario = Funcionario.objects.filter(matricula=request.user.matricula)
        funcionario, created = Funcionario.objects.get_or_create(matricula=request.user.matricula)

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

    try:
        funcionario = Funcionario.objects.get(matricula=request.user.matricula)
    except Funcionario.DoesNotExist as e:
        print('Usuário será adicionado como Funcionário')
        setor_funcionario = Setor.objects.get(nome="GESTAO DE PESSOAS")

        funcionario, created = Funcionario.objects.get_or_create(
            matricula=request.user.matricula,
            nome="ADM",
            setor=setor_funcionario
        )  

        if created:
            print(f"Funcionário de matricula {request.user.matricula} foi adicionado com sucesso")

    # Andamento de trilhas
    setor_do_usuario_object = Funcionario.objects.get(matricula=request.user.matricula)
    setor_do_usuario = setor_do_usuario_object.setor
    pastas = Pasta.objects.filter(Q(setores=setor_do_usuario) | Q(funcionarios__matricula=request.user.matricula)).distinct()

    progresso_trilha_individual_func = ProgressoTrilha(funcionario, pastas)
    progresso_pasta = progresso_trilha_individual_func.calcular_progresso_trilhas()

    progresso_trilha_individual_var = {
        'pastas': pastas,
        'progresso_pasta': progresso_pasta,
    }

    # Progresso geral individual
    progresso_valores = list(progresso_pasta.values())
    progresso_geral_individual = np.mean(progresso_valores) if progresso_valores else 0  # Evita média de lista vazia

    # Trilhas finalizadas
    trilhas_finalizadas = []
    for pasta in pastas:
        if progresso_pasta.get(pasta.nome) == 100:
            trilhas_finalizadas.append(pasta.nome)

    trilhas_finalizadas = str(len(trilhas_finalizadas)) + "/" + str(len(pastas))

    # Andamento por área
    media_progresso_area_trilha_individual = progresso_trilha_individual_func.calcular_media_progresso_area_trilha(progresso_pasta, pastas)
    if request.user.type == 'ADM':
        # Usuário é um administrador
        funcionario_logado = Funcionario.objects.filter(matricula=request.user.matricula)

        # Engajamento por funcionário
        funcionarios = Funcionario.objects.all()
        progresso_funcionarios = {}

        for funcionario in funcionarios:
            pastas = Pasta.objects.filter(Q(setores=funcionario.setor) | Q(funcionarios__matricula=funcionario.matricula))
            progresso_trilha = ProgressoTrilha(funcionario, pastas)
            progresso_pasta = progresso_trilha.calcular_progresso_trilhas()

            progresso_valores = list(progresso_pasta.values())
            progresso_geral = np.mean(progresso_valores) if progresso_valores else 0  # Evita média de lista vazia

            progresso_funcionarios[funcionario] = {
                'progresso': progresso_geral,
                'matricula': funcionario.matricula
            }


        # Último acesso por funcionário
        ultimos_acessos = CustomUser.objects.all().order_by('-last_login')

        # Últimas trilhas criadas
        ultimas_trilhas = Pasta.objects.all().order_by('-created_at')

    else:
        # Usuário é um líder
        funcionario_logado = Funcionario.objects.get(matricula=request.user.matricula)
        setor_funcionario_object = Funcionario.objects.get(matricula=request.user.matricula)
        setor_funcionario = setor_funcionario_object.setor

        # Engajamento por funcionário dentro do setor
        funcionarios = Funcionario.objects.filter(setor=setor_funcionario)
        progresso_funcionarios = {}

        # Processo apenas do setor do líder
        funcionarios_ids = [funcionario.matricula for funcionario in funcionarios]
        ultimos_acessos = CustomUser.objects.filter(matricula__in=funcionarios_ids).values('matricula', 'first_name', 'last_login').order_by('-last_login')

        for funcionario in funcionarios:
            pastas = Pasta.objects.filter(Q(setores=setor_funcionario) | Q(funcionarios__matricula=funcionario.matricula))
            progresso_trilha = ProgressoTrilha(funcionario, pastas)
            progresso_pasta = progresso_trilha.calcular_progresso_trilhas()

            progresso_valores = list(progresso_pasta.values())
            progresso_geral = np.mean(progresso_valores) if progresso_valores else 0  # Evita média de lista vazia

            progresso_funcionarios[funcionario] = {
                'progresso': progresso_geral,
                'matricula': funcionario.matricula
            }

        # Últimas trilhas criadas
        ultimas_trilhas = Pasta.objects.all().order_by('-created_at')

    # Definição do tipo de usuário
    user_type = 'Administrador' if request.user.type == 'ADM' else 'Líder'

    return render(request, 'home-superuser.html', {
        'user_type': user_type,
        'funcionario': funcionario_logado,
        'progresso_funcionarios': progresso_funcionarios,
        'ultimos_acessos': ultimos_acessos,
        'ultimas_trilhas': ultimas_trilhas,
        'media_progresso_area_trilha_individual': media_progresso_area_trilha_individual,
        'progresso_trilha': progresso_trilha,
        'progresso_geral_individual': progresso_geral_individual,
        'trilhas_finalizadas': trilhas_finalizadas,
        'progresso_trilha_individual': progresso_trilha_individual_var,
    })
