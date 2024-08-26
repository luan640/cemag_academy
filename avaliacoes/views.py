from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages

from .models import Prova, Questao, Alternativa, Resposta,ProvaRealizada, HistoricoProva
from cadastros.models import Funcionario
from materiais.models import Pasta
from users.models import CustomUser

from django.db.models import Sum

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

    if request.method == 'POST':

        prova = get_object_or_404(Prova, pk=pk)

        prova.delete()

        messages.success(request, 'Prova excluído com sucesso.')

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
        

def list_prova(request, pk):
    
    pasta = Pasta.objects.get(pk=pk)
    provas = Prova.objects.filter(pasta=pasta)   
    
    # Obtém o usuário atual e o funcionário correspondente
    funcionario = CustomUser.objects.get(matricula=request.user.matricula)

    # Dicionário para armazenar se o usuário realizou cada prova
    realizou_provas = {}  

    # Dicionário para armazenar os acertos por prova
    acertos_por_prova = {}

    validacao_do_certificado = 0
    baixar_certificado = False

    for prova in provas:
        realizou_prova = ProvaRealizada.objects.filter(usuario=request.user, prova=prova).exists()
        realizou_provas[prova.id] = realizou_prova  # Armazena True/False no dicionário
        total_respostas, total_questoes = calcular_nota(prova,funcionario)

        # Calcula o percentual de acerto
        percentual_acerto = (total_respostas/total_questoes) * 100 if total_questoes > 0 else 0
        acertos_por_prova[prova.id] = percentual_acerto
        if percentual_acerto >= 70:
            validacao_do_certificado += 1
    
    baixar_certificado = validacao_do_certificado == len(provas)
    prova_certificado = provas.first() if baixar_certificado and provas.exists() else None
        
    return render(request, 'provas/list-prova.html', {
        'pasta': pasta,
        'provas': provas,
        'acertos_por_prova': acertos_por_prova,  # Passa o dicionário para o template
        'realizou_provas':realizou_provas,
        'baixar_certificado': baixar_certificado,
        'prova_certificado':prova_certificado
    })

def realizar_prova(request, pk):
    prova = get_object_or_404(Prova, pk=pk)
    
    # Verificar se o usuário já realizou a prova
    if ProvaRealizada.objects.filter(usuario=request.user, prova=prova).exists():
        messages.info(request, "Você já realizou esta prova e não pode refazê-la.")
        return redirect('list-prova', pk=prova.pasta_id)

    questoes = prova.questao_prova.all()
    
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
        messages.success(request, "Prova realizada com sucesso!")
        
        return redirect('list-prova', pk=prova.pasta_id)

    return render(request, 'provas/realizar-prova.html', {
        'prova': prova,
        'questoes': questoes,
        'alternativas': alternativas_dict
    })

def visualizar_prova(request, pk):
    prova = get_object_or_404(Prova, pk=pk)
    questoes = prova.questao_prova.all()
    
    alternativas_dict = {}
    alternativas_selecionadas = {}  # Dicionário para armazenar IDs das alternativas selecionadas e respostas dissertativas

    for questao in questoes:
        # Obter alternativas para cada questão
        alternativas_questao = Alternativa.objects.filter(questao=questao)
        
        # Armazenar as alternativas no dicionário usando o ID da questão como chave
        alternativas_dict[questao.pk] = alternativas_questao

        # Tentar obter a resposta para a questão atual
        resposta = Resposta.objects.get(questao=questao, funcionario=request.user)
        
        if resposta.alternativa_selecionada_id is not None:
            alternativas_selecionadas[questao.pk] = resposta.alternativa_selecionada_id
        else:
            alternativas_selecionadas[questao.pk] = resposta.texto  # Adicionar o texto da resposta dissertativa

    return render(request, 'provas/visualizar-prova.html', {
        'prova': prova,
        'questoes': questoes,
        'alternativas': alternativas_dict,
        'alternativa_selecionada': alternativas_selecionadas  # Passar o dicionário de respostas selecionadas
    })

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
