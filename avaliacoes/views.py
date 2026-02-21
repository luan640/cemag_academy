from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.contrib.auth.decorators import login_required

from .models import Prova, Questao, Alternativa, Resposta,ProvaRealizada, HistoricoProva, AprovacaoTrilha
from cadastros.models import Funcionario
from materiais.models import Pasta
from users.models import CustomUser

from django.db.models import Sum, Q

from .forms import CorrigirRespostaDissertativaFormSet,CorrigirRespostaDissertativaForm

import json

def criar_prova(request, pk):

    pasta = get_object_or_404(Pasta, pk=pk)
        
    return render(request, 'provas/criar-prova.html', {
        'pasta':pasta
    })
    
@csrf_exempt
def salvar_prova(request, pk):
    if request.method == 'POST':
        data = json.loads(request.body)
        print(data)
        pasta = get_object_or_404(Pasta, pk=pk)
        prova = Prova.objects.create(pasta=pasta, titulo=data['titulo'], status=True)
        
        for questao_data in data['questoes']:
            questao = Questao.objects.create(prova=prova, enunciado=questao_data['enunciado'], tipo=questao_data['tipo'])
            
            if questao.tipo == 'objetiva':
                for alternativa_data in questao_data['alternativas']:
                    Alternativa.objects.create(
                        questao=questao,
                        texto=alternativa_data['texto'],
                        correta=alternativa_data['correta']
                    )
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

def delete_prova(request, pk):

    prova = get_object_or_404(Prova, pk=pk)

    prova.delete()

    return redirect('list-prova',pk=prova.pasta_id)

def calcular_nota(prova,funcionario):
    questoes = Questao.objects.filter(prova=prova)

    respostas = Resposta.objects.filter(
        questao__in=questoes, 
        funcionario=funcionario
    ).aggregate(total=Sum('nota'))

    # Obtém o total somado (retorna None se não houver respostas, por isso o `or 0`)
    total_respostas = respostas['total'] or 0

    # Conta o número total de questões da prova
    total_questoes = questoes.count()

    return total_respostas, total_questoes
        
def validacao_certificado(provas, matricula_funcionario):
    realizou_provas = {}  
    acertos_por_prova = {}

    # Dicionário que vai armazenar o status de certificação para cada pasta
    validacao_por_pasta = {}

    for prova in provas:
        realizou_prova = ProvaRealizada.objects.filter(usuario=matricula_funcionario, prova=prova).exists()
        realizou_provas[prova.id] = realizou_prova
        total_respostas, total_questoes = calcular_nota(prova, matricula_funcionario)

        percentual_acerto = (total_respostas / total_questoes) * 100 if total_questoes > 0 else 0
        acertos_por_prova[prova.id] = percentual_acerto

        # Usando o nome da pasta como chave
        pasta_nome = prova.pasta.nome

        # Se o nome da pasta ainda não está no dicionário, inicializa
        if pasta_nome not in validacao_por_pasta:
            validacao_por_pasta[pasta_nome] = {
                'pasta_id': prova.pasta.id,
                'certificado': True,  # Inicialmente consideramos que a pasta está certificada
                'provas': []
            }
        
        # Se o percentual de acertos for menor que 70%, a pasta não será certificada
        if percentual_acerto < 70:
            validacao_por_pasta[pasta_nome]['certificado'] = False  # Marca a pasta como não certificada

        # Adiciona o ID da prova à lista de provas associadas à pasta
        validacao_por_pasta[pasta_nome]['provas'].append(prova.id)

    return validacao_por_pasta, acertos_por_prova, realizou_provas

def list_prova(request, pk):
    
    pasta = Pasta.objects.get(pk=pk)
    provas = Prova.objects.filter(pasta=pasta)   
    
    # Obtém o usuário atual e o funcionário correspondente
    funcionario = CustomUser.objects.get(matricula=request.user.matricula)

    # Recebe os valores retornados, incluindo o dicionário de validação por pasta
    validacao_por_pasta, acertos_por_prova, realizou_provas = validacao_certificado(provas, funcionario)
    
    # Filtra apenas as pastas que foram certificadas (True no dicionário)
    pastas_certificadas = [pasta_data for pasta_nome, pasta_data in validacao_por_pasta.items() if pasta_data['certificado']]
    
    baixar_certificado = len(pastas_certificadas) > 0

    prova_certificada = provas.first() if baixar_certificado and provas.exists() else None

    provas_corrigidas = {prova.id: prova.respostas_corrigidas(funcionario) for prova in provas}

    total_provas = provas.count()
    provas_realizadas_count = sum(1 for prova in provas if realizou_provas.get(prova.id))
    provas_aprovadas = sum(
        1
        for prova in provas
        if realizou_provas.get(prova.id) and acertos_por_prova.get(prova.id, 0) >= prova.nota_minima
    )
    taxa_aprovacao = (provas_aprovadas / total_provas) * 100 if total_provas else 0
    media_acertos = (
        sum(acertos_por_prova.get(prova.id, 0) for prova in provas) / total_provas if total_provas else 0
    )
    
    return render(request, 'provas/list-prova.html', {
        'pasta': pasta,
        'provas': provas,
        'acertos_por_prova': acertos_por_prova,
        'realizou_provas': realizou_provas,
        'baixar_certificado': baixar_certificado,
        'prova_certificada': prova_certificada,  # Passa a lista de pastas certificadas para o template
        'provas_corrigidas':provas_corrigidas,
        'taxa_aprovacao': taxa_aprovacao,
        'provas_realizadas_count': provas_realizadas_count,
        'media_acertos': media_acertos,
        'total_provas': total_provas,
    })

def realizar_prova(request, pk):
    prova = get_object_or_404(Prova, pk=pk)
    
    # Verificar se o usuário já realizou a prova
    if ProvaRealizada.objects.filter(usuario=request.user, prova=prova).exists():
        messages.info(request, "Você já realizou esta prova e não pode refazê-la.")
        return redirect('list-prova', pk=prova.pasta_id)

    questoes = prova.questao_prova.all().order_by('id')
    
    alternativas_dict = {}
    
    for questao in questoes:
        # Para cada questão, obter suas alternativas
        alternativas_questao = Alternativa.objects.filter(questao=questao)
        # Armazenar as alternativas no dicionário usando o ID da questão como chave
        alternativas_dict[questao.pk] = alternativas_questao

    if request.method == 'POST':
        for questao in questoes:
            if questao.tipo == 'objetiva':
                alternativa_id = request.POST.get(f'questao_{questao.id}')
                if alternativa_id:
                    alternativa = get_object_or_404(Alternativa, id=alternativa_id)
                    nota = 1 if alternativa.correta else 0
                    Resposta.objects.create(
                        questao=questao,
                        funcionario=request.user,
                        alternativa_selecionada=alternativa,
                        nota=nota,
                        corrigida=True
                    )
            elif questao.tipo == 'dissertativa':
                texto = request.POST.get(f'questao_{questao.id}')
                Resposta.objects.create(
                    questao=questao,
                    funcionario=request.user,
                    texto=texto,
                    nota=0,
                    corrigida=False
                )
        
        ProvaRealizada.objects.create(usuario=request.user, prova=prova)
        # cria pendência de aprovação da trilha para líder
        AprovacaoTrilha.objects.get_or_create(
            usuario=request.user,
            pasta=prova.pasta,
            defaults={'status': 'pendente'}
        )
        messages.success(request, "Prova realizada com sucesso!")
        
        return redirect('list-prova', pk=prova.pasta_id)

    return render(request, 'provas/realizar-prova.html', {
        'pasta':prova.pasta,
        'prova': prova,
        'questoes': questoes,
        'alternativas': alternativas_dict
    })

@login_required
def aprovar_trilha_usuario(request, pasta_id, user_id):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método não permitido.'}, status=405)

    pasta = get_object_or_404(Pasta, pk=pasta_id)
    usuario = get_object_or_404(CustomUser, pk=user_id)

    # Permissão: ADM ou LID da mesma pasta/setor
    if request.user.type not in ('ADM', 'LID'):
        return JsonResponse({'success': False, 'error': 'Sem permissão.'}, status=403)
    if request.user.type == 'LID':
        try:
            if usuario.funcionario.setor_id != request.user.funcionario.setor_id:
                return JsonResponse({'success': False, 'error': 'Sem permissão.'}, status=403)
        except Exception:
            return JsonResponse({'success': False, 'error': 'Sem permissão.'}, status=403)

    aprovacao, _ = AprovacaoTrilha.objects.get_or_create(
        usuario=usuario,
        pasta=pasta,
        defaults={'status': 'pendente'}
    )
    aprovacao.status = 'aprovado'
    aprovacao.aprovado_por = request.user
    aprovacao.decidido_em = timezone.now()
    aprovacao.save()

    return JsonResponse({'success': True})

def visualizar_prova(request, pk,pk_matricula=0):
    prova = get_object_or_404(Prova, pk=pk)
    questoes = prova.questao_prova.all().order_by('id')
    
    alternativas_dict = {}
    alternativas_selecionadas = {}  # IDs selecionadas ou texto da dissertativa
    alternativas_certas = {}  # Alternativa correta
    nota_dissertativa = {}  # Notas das dissertativas
    dissertativa_status = {}

    for questao in questoes:
        # Obter alternativas para cada questão
        alternativas_questao = Alternativa.objects.filter(questao=questao)
        
        # Armazenar as alternativas no dicionário usando o ID da questão como chave
        alternativas_dict[questao.pk] = alternativas_questao

        # Tentar obter a resposta para a questão atual
        
        if pk_matricula != 0 and request.user.type == 'ADM':
            resposta = Resposta.objects.get(questao=questao, funcionario__matricula=pk_matricula)
            correta = alternativas_questao.filter(correta=True).first()
            alternativas_certas[questao.pk] = correta.id if correta else None
            nota_dissertativa[questao.pk] = resposta.nota
        else:
            resposta = Resposta.objects.get(questao=questao, funcionario=request.user)
            correta = alternativas_questao.filter(correta=True).first()
            alternativas_certas[questao.pk] = correta.id if correta else None
            if questao.tipo == 'dissertativa' and resposta.corrigida:
                nota_dissertativa[questao.pk] = resposta.nota

        if questao.tipo == 'dissertativa':
            status = None
            if resposta.corrigida and resposta.nota is not None:
                if resposta.nota >= 1:
                    status = 'correta'
                elif resposta.nota <= 0:
                    status = 'errada'
                else:
                    status = 'parcial'
            dissertativa_status[questao.pk] = status

        if resposta.alternativa_selecionada_id is not None:
            alternativas_selecionadas[questao.pk] = resposta.alternativa_selecionada_id
        else:
            alternativas_selecionadas[questao.pk] = resposta.texto  # Adicionar o texto da resposta dissertativa

    if pk_matricula != 0  and request.user.type == 'ADM':
        return render(request, 'provas/visualizar-prova.html', {
            'prova': prova,
            'questoes': questoes,
            'alternativas': alternativas_dict,
            'alternativa_selecionada': alternativas_selecionadas,  # Passar o dicionário de respostas selecionadas
            'alternativas_certas': alternativas_certas,  # Passar o dicionário de alternativas corretas
            'nota_dissertativa': nota_dissertativa,
            'dissertativa_status': dissertativa_status
        })
    else:
        return render(request, 'provas/visualizar-prova.html', {
            'prova': prova,
            'questoes': questoes,
            'alternativas': alternativas_dict,
            'alternativa_selecionada': alternativas_selecionadas,  # Passar o dicionário de respostas selecionadas
            'alternativas_certas': alternativas_certas,
            'nota_dissertativa': nota_dissertativa,
            'dissertativa_status': dissertativa_status
        })

def editar_prova(request, pk):
    # Edita o título da prova
    if request.method == 'POST':
        with transaction.atomic():

            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                return JsonResponse({"success": False, "error": "Formato JSON inválido"}, status=400)

            try:
                prova = Prova.objects.get(id=pk)
            except ObjectDoesNotExist:
                return JsonResponse({"success": False, "error": "Prova não encontrada" }, status=400)

            prova.titulo = data.get("titulo", prova.titulo)
            prova.save()

            return JsonResponse({"success":data}, status=200)

    elif request.method == 'GET':

        prova = get_object_or_404(Prova, pk=pk)
        questoes = prova.questao_prova.all().order_by('id')
        
        # Verificar se alguém já realizou esta prova
        prova_foi_realizada = ProvaRealizada.objects.filter(prova=prova).exists()
        
        alternativas_dict = {}

        for questao in questoes:
            # Obter alternativas para cada questão
            alternativas_questao = Alternativa.objects.filter(questao=questao)
            
            # Armazenar as alternativas no dicionário usando o ID da questão como chave
            alternativas_dict[questao.pk] = alternativas_questao

        return render(request, 'provas/editar-prova.html', {
            'prova': prova,
            'questoes': questoes,
            'alternativas': alternativas_dict,
            'prova_foi_realizada': prova_foi_realizada,
        })

def editar_questoes_alternativas(request, pk_questoes):
    if request.method != 'POST':
        return JsonResponse({"success": False, "error": "Método não permitido"}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Formato JSON inválido"}, status=400)

    try:
        with transaction.atomic():
            # Atualiza a questão
            try:
                questao_alterada = Questao.objects.get(id=pk_questoes)
            except ObjectDoesNotExist:
                return JsonResponse({"success": False, "error": "Questão não encontrada"}, status=404)
            
            # Verificar se a prova já foi realizada
            prova_foi_realizada = ProvaRealizada.objects.filter(prova=questao_alterada.prova).exists()
            if prova_foi_realizada:
                return JsonResponse({"success": False, "error": "Não é possível editar. A prova já foi realizada por alguém."}, status=403)

            questao_alterada.enunciado = data.get('enunciado', questao_alterada.enunciado)
            questao_alterada.save()

            # Processar alternativas
            alternativas_data = data.get('alternativas', [])
            alternativas_ids_recebidos = [alt.get('id') for alt in alternativas_data if alt.get('id')]
            
            # Excluir alternativas que não estão mais na lista (foram removidas)
            Alternativa.objects.filter(questao=questao_alterada).exclude(id__in=alternativas_ids_recebidos).delete()
            
            # Primeiro, desmarcar todas as alternativas como não corretas
            Alternativa.objects.filter(questao=questao_alterada).update(correta=False)
            
            # Atualizar ou criar alternativas
            alternativa_correta_id = data.get('alternativa_correta_id')
            alternativas_criadas = {}  # Para mapear IDs temporários para IDs reais
            
            for alternativa_data in alternativas_data:
                alternativa_id = alternativa_data.get('id')
                texto = alternativa_data.get('texto', '').strip()
                
                if not texto:
                    continue
                
                if alternativa_id:
                    # Atualizar alternativa existente
                    try:
                        alternativa = Alternativa.objects.get(id=alternativa_id, questao=questao_alterada)
                        alternativa.texto = texto
                        alternativa.correta = (str(alternativa_id) == str(alternativa_correta_id))
                        alternativa.save()
                    except Alternativa.DoesNotExist:
                        return JsonResponse({"success": False, "error": f"Alternativa {alternativa_id} não encontrada"}, status=404)
                else:
                    # Criar nova alternativa
                    nova_alt = Alternativa.objects.create(
                        questao=questao_alterada,
                        texto=texto,
                        correta=False
                    )
                    # Se esta alternativa tinha um ID temporário, mapear para o ID real
                    temp_id = alternativa_data.get('temp_id')
                    if temp_id:
                        alternativas_criadas[temp_id] = nova_alt.id
            
            # Se a alternativa correta era nova, atualizar usando o mapeamento
            if alternativa_correta_id and str(alternativa_correta_id).startswith('nova_'):
                real_id = alternativas_criadas.get(alternativa_correta_id)
                if real_id:
                    Alternativa.objects.filter(id=real_id).update(correta=True)

            return JsonResponse({"success": True}, status=200)

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)

def corrigir_questoes_dissertativas(request, pk_prova, pk_user):
    prova = get_object_or_404(Prova, pk=pk_prova)

    funcionario = get_object_or_404(CustomUser, matricula=pk_user)  # Busca o usuário pelo ID
    
    respostas_dissertativas = Resposta.objects.filter(
        questao__prova=prova, 
        questao__tipo='dissertativa', 
        funcionario=funcionario  # objeto Funcionario
    )
         
    if request.method == 'POST':
        formset = CorrigirRespostaDissertativaFormSet(request.POST, queryset=respostas_dissertativas)
        if formset.is_valid():
            formset.save()
            return redirect('list-participantes', pk=pk_prova)
    else:
        formset = CorrigirRespostaDissertativaFormSet(queryset=respostas_dissertativas)
    
    questoes_e_respostas = []
    for form, resposta in zip(formset.forms, respostas_dissertativas):
        questoes_e_respostas.append(
            (form, resposta.questao.enunciado, resposta.texto)  # Inclui o enunciado na tupla
        )   
        
    context = {
        'formset': formset,
        'prova': prova,
        'funcionario': funcionario,
        'questoes_e_respostas': questoes_e_respostas,  # Passa a lista modificada
    }
        
    return render(request, 'provas/corrigir_questoes_dissertativas.html', context)

def refazer_prova(request, pk_prova,pk_user):
    prova = get_object_or_404(Prova, pk=pk_prova)
    id_pasta = prova.pasta.id

    funcionario = get_object_or_404(CustomUser, matricula=pk_user)  # Busca o usuário pelo ID

    prova_realizada = ProvaRealizada.objects.get(prova=prova, usuario=funcionario)

    respostas_anteriores = Resposta.objects.filter(
        questao__prova=prova, 
        funcionario=funcionario  # objeto Funcionario
    )
    
    # Obtém o objeto Pasta correspondente ao id_pasta
    pasta = get_object_or_404(Pasta, id=id_pasta)

    total_respostas, total_questoes = calcular_nota(prova,funcionario)
    # Calcula o percentual de acerto
    nota_final = (total_respostas/total_questoes) * 10 if total_questoes > 0 else 0

    HistoricoProva.objects.create(
        pasta=pasta,
        data_realizacao=prova_realizada.data_realizacao,
        nota_final=nota_final
    )

    prova_realizada.delete()
    respostas_anteriores.delete()
    
    return redirect('list-prova', pk=prova.pasta_id)


def provas_pendentes_usuario(request):
    usuario = request.user
    provas_pendentes = Prova.objects.filter(Q(status='ativa') | Q(status=True)).exclude(provarealizada__usuario=usuario)

    return render(request, 'provas/provas-pendentes.html', {
        'provas_pendentes': provas_pendentes
    })
