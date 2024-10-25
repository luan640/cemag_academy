from django.shortcuts import render,get_object_or_404,redirect
from django.contrib.auth.decorators import login_required,user_passes_test
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.core.cache import cache
from django.db.models import Count, Q

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

    if request.user.type in ['ADM','LID','DIR']:
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
        print(setor_funcionario)

        funcionario, created = Funcionario.objects.get_or_create(
            matricula=request.user.matricula,
            nome="ADM",
            setor=setor_funcionario
        )  

        if created:
            print(f"Funcionário de matricula {funcionario.matricula} foi adicionado com sucesso")

    return render(request, 'home-superuser.html')

def ultimas_trilhas(request):
    ultimas_trilhas = Pasta.objects.all().order_by('-created_at')[:5]
    html_content = render_to_string('partials/card_ultimas_trilhas.html', {
        'ultimas_trilhas': ultimas_trilhas,
    })

    return JsonResponse({'html': html_content})

def ultimos_acessos(request):

    if request.user.type == 'ADM':
        ultimos_acessos = CustomUser.objects.filter(last_login__isnull=False).order_by('-last_login')
    else:
        setor_funcionario = Funcionario.objects.get(matricula=request.user.matricula).setor
        funcionarios = Funcionario.objects.filter(setor=setor_funcionario)
        funcionarios_ids = [funcionario.matricula for funcionario in funcionarios]
        
        ultimos_acessos = CustomUser.objects.filter(
            matricula__in=funcionarios_ids,
            last_login__isnull=False
        ).values('matricula', 'first_name', 'last_login').order_by('-last_login')[:5]
    
    html_content = render_to_string('partials/card_ultimos_acessos.html', {
        'ultimos_acessos': ultimos_acessos,
    })
    return JsonResponse({'html': html_content})
    
# Função para carregar trilhas finalizadas
def load_trilhas_finalizadas(request):
    try:
        setor_do_usuario = get_setor_do_usuario(request.user)
        pastas = get_pastas(setor_do_usuario, request.user.matricula)

        progresso_trilha_individual = calcular_progresso_trilha_individual(request.user, pastas)
        trilhas_finalizadas = calcular_trilhas_finalizadas(pastas, progresso_trilha_individual['progresso_pasta'])

    except Funcionario.DoesNotExist:
        trilhas_finalizadas = f"Campo de trilhas para os colaboradores"

    html_content = render_to_string('partials/trilhas_finalizadas.html', {
        'trilhas_finalizadas': trilhas_finalizadas,
    })

    return JsonResponse({'html': html_content})

# Função para carregar progresso geral individual
def load_progresso_geral_individual(request):
    try:
        setor_do_usuario = get_setor_do_usuario(request.user)
        pastas = get_pastas(setor_do_usuario, request.user.matricula)

        progresso_trilha_individual = calcular_progresso_trilha_individual(request.user, pastas)
        progresso_geral_individual = progresso_trilha_individual['progresso_geral_individual']
    except Funcionario.DoesNotExist:
        progresso_geral_individual = "Progresso geral de trilhas por colaborador"

    html_content = render_to_string('partials/progresso_geral_individual.html', {
        'progresso_geral_individual': progresso_geral_individual,
    })

    return JsonResponse({'html': html_content})


# Função para carregar progresso dos funcionários
def load_progresso_funcionarios(request):

    progresso_funcionarios = get_leader_data(request.user)

    html_content = render_to_string('partials/progresso_funcionarios.html', {
        'progresso_funcionarios': progresso_funcionarios,
    })

    return JsonResponse({'html': html_content})

def get_setor_do_usuario(user):
    funcionario = Funcionario.objects.get(matricula=user.matricula)
    return funcionario.setor

def get_pastas(setor_do_usuario, matricula):
    return Pasta.objects.filter(Q(setores=setor_do_usuario) | Q(funcionarios__matricula=matricula)).distinct()

def calcular_progresso_trilha_individual(user, pastas):
    cache_key = f"progresso_trilha_{user.matricula}"
    progresso_cache = cache.get(cache_key)
    if progresso_cache:
        return progresso_cache

    progresso_trilha = ProgressoTrilha(Funcionario.objects.get(matricula=user.matricula), pastas)
    progresso_pasta = progresso_trilha.calcular_progresso_trilhas()
    progresso_valores = list(progresso_pasta.values())
    progresso_geral_individual = np.mean(progresso_valores) if progresso_valores else 0

    progresso_cache = {
        'pastas': pastas,
        'progresso_pasta': progresso_pasta,
        'progresso_geral_individual': progresso_geral_individual,
    }
    cache.set(cache_key, progresso_cache, timeout=3600)  # 1 hora de cache

    return progresso_cache

def calcular_trilhas_finalizadas(pastas, progresso_pasta):
    trilhas_finalizadas = [pasta.nome for pasta in pastas if progresso_pasta.get(pasta.nome) == 100]
    return f"{len(trilhas_finalizadas)}/{len(pastas)}"

def calcular_media_progresso_area_trilha(user, pastas, progresso_pasta):
    progresso_trilha_individual_func = ProgressoTrilha(Funcionario.objects.get(matricula=user.matricula), pastas)
    return progresso_trilha_individual_func.calcular_media_progresso_area_trilha(progresso_pasta, pastas)

def get_leader_data(user):
    setor_funcionario = Funcionario.objects.select_related('setor').get(matricula=user.matricula).setor
    funcionarios = Funcionario.objects.filter(
        setor=setor_funcionario
    ).select_related('setor', 'user').exclude(user__type='ADM')
    print(funcionarios)
    return get_progresso(funcionarios)

def get_adm_data():
    funcionarios = Funcionario.objects.select_related('setor').all().order_by('nome')
    return get_progresso(funcionarios)

def get_progresso(funcionarios):
    progresso_funcionarios = {}
    pastas_cache = {}

    for funcionario in funcionarios:
        # Tente obter as pastas do cache ou chame a função get_pastas
        pastas = pastas_cache.get(funcionario.setor) or get_pastas(funcionario.setor, funcionario.matricula)
        pastas_cache[funcionario.setor] = pastas

        # Calcular progresso
        progresso_trilha = ProgressoTrilha(funcionario, pastas)
        progresso_pasta = progresso_trilha.calcular_progresso_trilhas()

        # Calcular progresso geral
        progresso_valores = list(progresso_pasta.values())
        progresso_geral = np.mean(progresso_valores) if progresso_valores else 0

        progresso_funcionarios[funcionario] = {
            'progresso': progresso_geral,
            'matricula': funcionario.matricula,
            'progress_pasta': progresso_pasta
        }

    return progresso_funcionarios