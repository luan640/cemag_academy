from django.shortcuts import render,get_object_or_404,redirect
from django.contrib.auth.decorators import login_required,user_passes_test
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.core.cache import cache
from django.db.models import Count, Q

from cadastros.models import Funcionario
from materiais.models import Pasta,Material,Visualizacao,Setor,RespostaAvaliacaoEficacia
from users.models import CustomUser
from materiais.utils import ProgressoTrilha
from avaliacoes.models import Prova, ProvaRealizada, Resposta, AprovacaoTrilha
from biblioteca.models import Livro

import time
import numpy as np
import json

# def assiduidade_por_setor_api(request):
#     setores = Setor.objects.all()
#     assiduidade_por_setor = {}

#     for setor in setores:
#         # Funcion├írios do setor
#         funcionarios_setor = Funcionario.objects.filter(setor=setor)
#         total_funcionarios = funcionarios_setor.count()

#         if total_funcionarios > 0:
#             # Quantidade total de materiais dispon├¡veis para o setor
#             total_materiais_setor = Material.objects.filter(pasta__setores=setor).count()

#             if total_materiais_setor > 0:
#                 # Quantidade total de visualiza├º├Áes por funcion├írios do setor
#                 total_visualizacoes = Visualizacao.objects.filter(funcionario__in=funcionarios_setor, pasta__setores=setor).count()
                
#                 # Calculando a propor├º├úo de visualiza├º├Áes
#                 proporcao_visualizacao = (total_visualizacoes / (total_funcionarios * total_materiais_setor)) * 100
#                 assiduidade_por_setor[setor.nome] = f"{proporcao_visualizacao:.2f}%"
#             else:
#                 assiduidade_por_setor[setor.nome] = "Nenhum material dispon├¡vel"
#         else:
#             assiduidade_por_setor[setor.nome] = "Nenhum funcion├írio no setor"

#     return JsonResponse(assiduidade_por_setor)

# def trilhas_por_setor_api(request):
#     if request.method == 'POST':
#         try:
#             # Ler o corpo da solicita├º├úo JSON
#             data = json.loads(request.body)
#             setor_nome = data.get('setor')  # Nome do setor enviado no corpo da solicita├º├úo
            
#             # Verifica se o setor foi fornecido
#             if not setor_nome:
#                 return JsonResponse({'error': 'Setor n├úo fornecido'}, status=400)

#             # Tenta encontrar o setor
#             setor = get_object_or_404(Setor, nome=setor_nome)

#             # Conta as pastas associadas ao setor espec├¡fico
#             pastas_setor = Pasta.objects.filter(setores=setor)
#             trilhas_por_setor = {setor.nome: pastas_setor.count()}
            
#             return JsonResponse(trilhas_por_setor)

#         except json.JSONDecodeError:
#             return JsonResponse({'error': 'Formato JSON inv├ílido'}, status=400)
#     else:
#         # Para GET ou outras requisi├º├Áes, retorna todas as trilhas
#         setores = Setor.objects.all()
#         trilhas_por_setor = {}

#         for setor in setores:
#             pastas_setor = Pasta.objects.filter(setores=setor)
#             trilhas_por_setor[setor.nome] = pastas_setor.count()

#         return JsonResponse(trilhas_por_setor)
    
@login_required
def painel_home(request):

    # funcionario = Funcionario.objects.filter(matricula=request.user.matricula)
    funcionario, created = Funcionario.objects.get_or_create(matricula=request.user.matricula)

    #Andamento de trilhas
    #pastas que o usuario tem acesso
    setor_do_usuario_object = Funcionario.objects.get(matricula=request.user.matricula)
    setor_do_usuario = setor_do_usuario_object.setor
    pastas = Pasta.objects.filter(Q(setores=setor_do_usuario) | Q(funcionarios__matricula=request.user.matricula)).distinct()

    
    pendencias_trilhas = []
    # Pastas concluidas pelo usuario (100% materiais vistos)
    materiais_count = Material.objects.filter(pasta__in=pastas).values('pasta_id').annotate(total=Count('id'))
    visualizacoes_count = Visualizacao.objects.filter(
        funcionario__matricula=request.user.matricula,
        material__pasta__in=pastas
    ).values('material__pasta_id').annotate(total=Count('id'))
    materiais_map = {m['pasta_id']: m['total'] for m in materiais_count}
    visualizacoes_map = {v['material__pasta_id']: v['total'] for v in visualizacoes_count}
    pastas_concluidas_ids = [
        pasta.id for pasta in pastas
        if materiais_map.get(pasta.id, 0) > 0 and visualizacoes_map.get(pasta.id, 0) >= materiais_map.get(pasta.id, 0)
    ]

    pendencias_provas = Prova.objects.filter(
        Q(status='ativa') | Q(status=True),
        pasta__in=pastas_concluidas_ids
    ).exclude(provarealizada__usuario=request.user)
    pendencias_avaliacoes = []
    pendencias_correcao = []
    pendencias_aprovacao = []
    if request.user.type in ['ADM', 'LID']:
        respostas_pendentes = Resposta.objects.filter(
            questao__tipo='dissertativa',
            corrigida=False
        )
        if request.user.type == 'LID':
            respostas_pendentes = respostas_pendentes.filter(
                funcionario__type='LEI',
                funcionario__funcionario__setor=setor_do_usuario
            )
        pendencias_correcao = list(
            respostas_pendentes.values(
                'questao__prova_id',
                'questao__prova__titulo',
                'questao__prova__pasta__nome',
                'funcionario__matricula',
                'funcionario__first_name',
                'funcionario__last_name'
            ).annotate(total=Count('id')).order_by('-total')
        )
        aprovacao_qs = AprovacaoTrilha.objects.filter(status='pendente')
        if request.user.type == 'LID':
            aprovacao_qs = aprovacao_qs.filter(
                usuario__type='LEI',
                usuario__funcionario__setor=setor_do_usuario
            )
        pendencias_aprovacao = list(aprovacao_qs.values(
            'usuario__id',
            'usuario__matricula',
            'usuario__first_name',
            'usuario__last_name',
            'pasta__id',
            'pasta__nome',
            'criado_em'
        ).order_by('-criado_em'))
    pastas_usuario = Pasta.objects.filter(
        Q(created_by=request.user) |
        Q(funcionarios__matricula=request.user.matricula) |
        Q(setores=setor_do_usuario)
    ).distinct().order_by('-created_at')[:5]
    livros = Livro.objects.order_by('-created_at')[:5]

    # Últimas provas corrigidas
    provas_realizadas = ProvaRealizada.objects.filter(usuario=request.user).select_related('prova__pasta').order_by('-data_realizacao')[:20]
    provas_corrigidas_recentes = []
    for pr in provas_realizadas:
        if pr.prova.respostas_corrigidas(request.user):
            possui_comentario = Resposta.objects.filter(
                questao__prova=pr.prova,
                funcionario=request.user,
                comentario__isnull=False
            ).exclude(comentario='').exists()
            provas_corrigidas_recentes.append({
                'id': pr.prova.id,
                'titulo': pr.prova.titulo,
                'pasta': pr.prova.pasta.nome,
                'data': pr.data_realizacao,
                'possui_comentario': possui_comentario,
            })

    provas_corrigidas_recentes = provas_corrigidas_recentes[:5]

    return render(request,
                'home.html', {
                'funcionario':funcionario,
                'pastas_usuario': pastas_usuario,
                'livros': livros,
                'pendencias_trilhas': pendencias_trilhas,
                'pendencias_provas': pendencias_provas,
                'pendencias_avaliacoes': pendencias_avaliacoes,
                'pendencias_correcao': pendencias_correcao,
                'pendencias_aprovacao': pendencias_aprovacao,
                'provas_corrigidas_recentes': provas_corrigidas_recentes,
            })

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
    
# Fun├º├úo para carregar trilhas finalizadas
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

# Fun├º├úo para carregar progresso geral individual
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


# Fun├º├úo para carregar progresso dos funcion├írios
def load_progresso_funcionarios(request):

    progresso_funcionarios = get_leader_data(request.user)

    html_content = render_to_string('partials/progresso_funcionarios.html', {
        'progresso_funcionarios': progresso_funcionarios,
    })

    return JsonResponse({'html': html_content})

@login_required
def load_home_progress(request):
    try:
        setor_do_usuario = get_setor_do_usuario(request.user)
        pastas = get_pastas(setor_do_usuario, request.user.matricula)
        progresso_trilha_individual = calcular_progresso_trilha_individual(request.user, pastas)
        progresso_pasta = progresso_trilha_individual.get('progresso_pasta', {})
        progresso_geral = progresso_trilha_individual.get('progresso_geral_individual', 0)
        pendencias_trilhas = [p for p in pastas if progresso_pasta.get(p.nome, 0) < 100]
    except Funcionario.DoesNotExist:
        pendencias_trilhas = []
        progresso_geral = 0

    html_content = render_to_string('partials/home_trilhas_pendentes.html', {
        'pendencias_trilhas': pendencias_trilhas,
    })

    return JsonResponse({
        'html': html_content,
        'progresso_geral': round(progresso_geral),
        'trilhas_pendentes_count': len(pendencias_trilhas),
    })

@login_required
def load_home_avaliacoes(request):
    try:
        setor_do_usuario = get_setor_do_usuario(request.user)
        pastas = list(get_pastas(setor_do_usuario, request.user.matricula))
        materiais_count = Material.objects.filter(pasta__in=pastas).values('pasta_id').annotate(total=Count('id'))
        visualizacoes_count = Visualizacao.objects.filter(
            funcionario__matricula=request.user.matricula,
            material__pasta__in=pastas
        ).values('material__pasta_id').annotate(total=Count('id'))
        materiais_map = {m['pasta_id']: m['total'] for m in materiais_count}
        visualizacoes_map = {v['material__pasta_id']: v['total'] for v in visualizacoes_count}
        provas_realizadas_map = set(
            ProvaRealizada.objects.filter(usuario=request.user, prova__pasta__in=pastas).values_list('prova__pasta_id', flat=True)
        )
        pastas_finalizadas = []
        for p in pastas:
            total_mat = materiais_map.get(p.id, 0)
            vistos = visualizacoes_map.get(p.id, 0)
            progresso_ok = total_mat > 0 and vistos >= total_mat
            if progresso_ok or p.id in provas_realizadas_map:
                pastas_finalizadas.append(p)
        pastas_finalizadas_ids = [p.id for p in pastas_finalizadas]
        respondidas_ids = set(
            RespostaAvaliacaoEficacia.objects.filter(
                usuario=request.user,
                avaliacao_eficacia__pasta_id__in=pastas_finalizadas_ids
            ).values_list('avaliacao_eficacia__pasta_id', flat=True)
        )
        pendencias_avaliacoes = [p for p in pastas_finalizadas if p.id not in respondidas_ids]
    except Funcionario.DoesNotExist:
        pendencias_avaliacoes = []

    html_content = render_to_string('partials/home_avaliacoes_pendentes.html', {
        'pendencias_avaliacoes': pendencias_avaliacoes,
    })

    return JsonResponse({
        'html': html_content,
        'avaliacoes_pendentes_count': len(pendencias_avaliacoes),
    })

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
        # Tente obter as pastas do cache ou chame a fun├º├úo get_pastas
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
