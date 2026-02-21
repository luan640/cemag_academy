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
from biblioteca.models import Livro, Rating

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
    from django.db.models import Prefetch, Subquery, OuterRef, Exists
    
    # Obter funcionário com setor em uma única query
    funcionario = Funcionario.objects.select_related('setor').get_or_create(
        matricula=request.user.matricula
    )[0]
    setor_do_usuario = funcionario.setor

    # Pastas que o usuário tem acesso - otimizado
    pastas = Pasta.objects.filter(
        Q(setores=setor_do_usuario) | Q(funcionarios__matricula=request.user.matricula)
    ).distinct().select_related('created_by')

    # Otimização: Calcular pastas concluídas com annotations
    pastas_com_counts = pastas.annotate(
        total_materiais=Count('pasta_material', distinct=True),
        materiais_vistos=Count(
            'pasta_material__visualizacoes',
            filter=Q(pasta_material__visualizacoes__funcionario=funcionario),
            distinct=True
        )
    )
    
    # IDs das pastas concluídas (100% materiais vistos)
    pastas_concluidas_ids = [
        p.id for p in pastas_com_counts 
        if p.total_materiais > 0 and p.materiais_vistos >= p.total_materiais
    ]

    # Pendências de provas - otimizado com select_related
    pendencias_provas = Prova.objects.filter(
        Q(status='ativa') | Q(status=True),
        pasta_id__in=pastas_concluidas_ids
    ).exclude(
        provarealizada__usuario=request.user
    ).select_related('pasta').distinct()

    pendencias_trilhas = []
    pendencias_avaliacoes = []
    pendencias_correcao = []
    pendencias_aprovacao = []

    # Pendências de correção e aprovação para ADM/LID
    if request.user.type in ['ADM', 'LID']:
        # Correções pendentes - otimizado
        respostas_pendentes = Resposta.objects.filter(
            questao__tipo='dissertativa',
            corrigida=False
        ).select_related(
            'questao__prova__pasta',
            'funcionario__funcionario__setor'
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
            ).annotate(total=Count('id')).order_by('-total')[:20]
        )

        # Aprovações pendentes - otimizado
        aprovacao_qs = AprovacaoTrilha.objects.filter(
            status='pendente'
        ).select_related(
            'usuario__funcionario__setor',
            'pasta'
        )
        
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
        ).order_by('-criado_em')[:20])

    # Últimas pastas do usuário - otimizado com progresso
    pastas_usuario = Pasta.objects.filter(
        Q(created_by=request.user) |
        Q(funcionarios__matricula=request.user.matricula) |
        Q(setores=setor_do_usuario)
    ).distinct().select_related('created_by').annotate(
        total_materiais=Count('pasta_material', distinct=True),
        total_arquivos_drive=Count('arquivosdrive', distinct=True),
        visualizacoes_count=Count(
            'pasta_material__visualizacoes',
            filter=Q(pasta_material__visualizacoes__funcionario=funcionario),
            distinct=True
        )
    ).order_by('-created_at')[:5]
    
    # Calcular progresso para cada pasta
    for pasta in pastas_usuario:
        total = pasta.total_materiais + pasta.total_arquivos_drive
        if total > 0:
            pasta.progresso = int((pasta.visualizacoes_count / total) * 100)
        else:
            pasta.progresso = 0
    
    # Últimos livros
    livros = Livro.objects.order_by('-created_at')[:5]
    
    # Adicionar rating information para cada livro
    for livro in livros:
        user_rating = livro.ratings.filter(user=request.user).first()
        ratings = livro.ratings.all()

        if ratings:
            media_ratings = sum(r.score for r in ratings) / len(ratings)
        else:
            media_ratings = 0 

        livro.media_ratings = media_ratings

        if user_rating:
            livro.user_rating = user_rating.score
        else:
            livro.user_rating = 0

    # Últimas provas corrigidas - OTIMIZADO (principal gargalo removido!)
    provas_realizadas = ProvaRealizada.objects.filter(
        usuario=request.user
    ).select_related('prova__pasta').order_by('-data_realizacao')[:20]
    
    # Pré-carregar todas as informações de respostas em uma query
    provas_ids = [pr.prova_id for pr in provas_realizadas]
    
    # Query otimizada: buscar todas as respostas de uma vez
    respostas_info = Resposta.objects.filter(
        questao__prova_id__in=provas_ids,
        funcionario=request.user,
        questao__tipo='dissertativa'
    ).values('questao__prova_id').annotate(
        total=Count('id'),
        corrigidas=Count('id', filter=Q(corrigida=True)),
        com_comentario=Count('id', filter=Q(comentario__isnull=False) & ~Q(comentario=''))
    )
    
    # Criar mapa de respostas por prova
    respostas_map = {r['questao__prova_id']: r for r in respostas_info}
    
    # Query otimizada: contar questões dissertativas por prova
    questoes_dissertativas = Resposta.objects.filter(
        questao__prova_id__in=provas_ids,
        questao__tipo='dissertativa'
    ).values('questao__prova_id').annotate(
        total_questoes=Count('questao_id', distinct=True)
    )
    questoes_map = {q['questao__prova_id']: q['total_questoes'] for q in questoes_dissertativas}
    
    provas_corrigidas_recentes = []
    for pr in provas_realizadas:
        prova_id = pr.prova_id
        info = respostas_map.get(prova_id, {})
        total_questoes = questoes_map.get(prova_id, 0)
        
        # Verifica se todas as questões dissertativas foram corrigidas
        if total_questoes > 0 and info.get('corrigidas', 0) >= total_questoes:
            provas_corrigidas_recentes.append({
                'id': pr.prova.id,
                'titulo': pr.prova.titulo,
                'pasta': pr.prova.pasta.nome,
                'data': pr.data_realizacao,
                'possui_comentario': info.get('com_comentario', 0) > 0,
            })
            
            if len(provas_corrigidas_recentes) >= 5:
                break

    return render(request, 'home.html', {
        'funcionario': funcionario,
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
    ultimas_trilhas = Pasta.objects.select_related('created_by').order_by('-created_at')[:5]
    html_content = render_to_string('partials/card_ultimas_trilhas.html', {
        'ultimas_trilhas': ultimas_trilhas,
    })
    return JsonResponse({'html': html_content})

def ultimos_acessos(request):
    if request.user.type == 'ADM':
        ultimos_acessos = CustomUser.objects.filter(
            last_login__isnull=False
        ).order_by('-last_login')[:5]
    else:
        setor_funcionario = Funcionario.objects.select_related('setor').get(
            matricula=request.user.matricula
        ).setor
        
        # Otimizado: uma única query com values
        ultimos_acessos = CustomUser.objects.filter(
            funcionario__setor=setor_funcionario,
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
        # Cache para melhorar performance
        cache_key = f'home_progress_{request.user.matricula}'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return JsonResponse(cached_data)
        
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

    result = {
        'html': html_content,
        'progresso_geral': round(progresso_geral),
        'trilhas_pendentes_count': len(pendencias_trilhas),
    }
    
    # Cache por 10 minutos
    cache.set(cache_key, result, timeout=600)
    
    return JsonResponse(result)

@login_required
def load_home_avaliacoes(request):
    try:
        # Cache para melhorar performance
        cache_key = f'home_avaliacoes_{request.user.matricula}'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return JsonResponse(cached_data)
        
        funcionario = Funcionario.objects.select_related('setor').get(matricula=request.user.matricula)
        setor_do_usuario = funcionario.setor
        
        # Otimizado: usar annotate direto
        pastas = Pasta.objects.filter(
            Q(setores=setor_do_usuario) | Q(funcionarios__matricula=request.user.matricula)
        ).distinct().annotate(
            total_materiais=Count('pasta_material', distinct=True),
            materiais_vistos=Count(
                'pasta_material__visualizacoes',
                filter=Q(pasta_material__visualizacoes__funcionario=funcionario),
                distinct=True
            )
        )
        
        # IDs das pastas finalizadas
        pastas_finalizadas_ids = [
            p.id for p in pastas 
            if p.total_materiais > 0 and p.materiais_vistos >= p.total_materiais
        ]
        
        # Também incluir pastas onde o usuário já fez prova
        provas_realizadas_ids = set(
            ProvaRealizada.objects.filter(
                usuario=request.user
            ).values_list('prova__pasta_id', flat=True)
        )
        
        pastas_finalizadas_ids = list(set(pastas_finalizadas_ids) | provas_realizadas_ids)
        
        # IDs das avaliações já respondidas pelo usuário (buscar todas, não apenas das finalizadas)
        respondidas_ids = set(
            RespostaAvaliacaoEficacia.objects.filter(
                usuario=request.user
            ).values_list('avaliacao_eficacia__pasta_id', flat=True)
        )
        
        # Pendências de avaliações
        pendencias_avaliacoes = Pasta.objects.filter(
            id__in=pastas_finalizadas_ids
        ).exclude(
            id__in=respondidas_ids
        ).select_related('created_by')[:20]
        
    except Funcionario.DoesNotExist:
        pendencias_avaliacoes = []

    html_content = render_to_string('partials/home_avaliacoes_pendentes.html', {
        'pendencias_avaliacoes': pendencias_avaliacoes,
    })

    result = {
        'html': html_content,
        'avaliacoes_pendentes_count': pendencias_avaliacoes.count() if hasattr(pendencias_avaliacoes, 'count') else len(pendencias_avaliacoes),
    }
    
    # Cache por 10 minutos
    cache.set(cache_key, result, timeout=600)
    
    return JsonResponse(result)

def get_setor_do_usuario(user):
    # Cache do setor do usuário
    cache_key = f'setor_usuario_{user.matricula}'
    setor = cache.get(cache_key)
    
    if not setor:
        funcionario = Funcionario.objects.select_related('setor').get(matricula=user.matricula)
        setor = funcionario.setor
        cache.set(cache_key, setor, timeout=3600)  # Cache de 1 hora
    
    return setor

def get_pastas(setor_do_usuario, matricula):
    # Cache das pastas do usuário
    cache_key = f'pastas_usuario_{matricula}'
    pastas = cache.get(cache_key)
    
    if not pastas:
        pastas = Pasta.objects.filter(
            Q(setores=setor_do_usuario) | Q(funcionarios__matricula=matricula)
        ).distinct().select_related('created_by')
        cache.set(cache_key, pastas, timeout=1800)  # Cache de 30 minutos
    
    return pastas

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
    # Cache dos dados do líder
    cache_key = f'leader_data_{user.matricula}'
    cached_data = cache.get(cache_key)
    
    if cached_data:
        return cached_data
    
    setor_funcionario = Funcionario.objects.select_related('setor').get(
        matricula=user.matricula
    ).setor
    
    funcionarios = Funcionario.objects.filter(
        setor=setor_funcionario
    ).select_related('setor').prefetch_related('user').exclude(user__type='ADM')
    
    progresso_data = get_progresso(funcionarios)
    
    # Cache por 30 minutos
    cache.set(cache_key, progresso_data, timeout=1800)
    
    return progresso_data

def get_adm_data():
    # Cache dos dados do admin
    cache_key = 'adm_data_all'
    cached_data = cache.get(cache_key)
    
    if cached_data:
        return cached_data
    
    funcionarios = Funcionario.objects.select_related('setor').all().order_by('nome')
    progresso_data = get_progresso(funcionarios)
    
    # Cache por 30 minutos
    cache.set(cache_key, progresso_data, timeout=1800)
    
    return progresso_data

def get_progresso(funcionarios):
    progresso_funcionarios = {}
    pastas_cache = {}

    # Otimização: pré-carregar todas as pastas de todos os setores de uma vez
    setores_ids = list(set(f.setor_id for f in funcionarios if f.setor_id))
    matriculas = [f.matricula for f in funcionarios]
    
    # Query única para buscar todas as pastas relevantes
    todas_pastas = Pasta.objects.filter(
        Q(setores__id__in=setores_ids) | Q(funcionarios__matricula__in=matriculas)
    ).distinct().select_related('created_by').prefetch_related('setores', 'funcionarios')
    
    # Criar mapa de pastas por setor e funcionário
    pastas_por_setor = {}
    pastas_por_funcionario = {}
    
    for pasta in todas_pastas:
        for setor in pasta.setores.all():
            if setor.id not in pastas_por_setor:
                pastas_por_setor[setor.id] = []
            pastas_por_setor[setor.id].append(pasta)
        
        for func in pasta.funcionarios.all():
            if func.matricula not in pastas_por_funcionario:
                pastas_por_funcionario[func.matricula] = []
            pastas_por_funcionario[func.matricula].append(pasta)

    for funcionario in funcionarios:
        # Usar pastas do cache
        pastas_setor = pastas_por_setor.get(funcionario.setor_id, [])
        pastas_func = pastas_por_funcionario.get(funcionario.matricula, [])
        pastas = list(set(pastas_setor + pastas_func))

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
