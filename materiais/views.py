from django.shortcuts import render, redirect,get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.db.models import Count, Q
from django.db import connection
from django.http import HttpResponse
from django.template.loader import get_template
from django.conf import settings  # Importe o módulo settings
from django.core.mail import send_mail,EmailMultiAlternatives
from django.core import serializers
import json

from .models import Pasta,Material,Visualizacao,AvaliacaoEficacia, RespostaAvaliacaoEficacia,Certificado
from avaliacoes.views import calcular_nota,validacao_certificado
from .forms import AddPasta,AddMaterial,VisualizacaoForm
from cadastros.models import Funcionario,Setor
from biblioteca.models import VisualizacaoLivro, Rating
from avaliacoes.models import ProvaRealizada, Prova
from users.models import CustomUser
from cemag_academy.settings.base import *

from reportlab.pdfgen import canvas
import re
import environ
from io import BytesIO
from xhtml2pdf import pisa  # Importa o conversor de HTML para PDF
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, PageTemplate, Frame

def extrair_id_youtube(url):
    regex = r"(?:https?:\/\/)?(?:www\.)?(?:youtube\.com|youtu\.be)\/(?:watch\?v=)?(.{11})"
    match = re.match(regex, url)
    if match:
        return match.group(1)
    return None

def is_id_youtube_valido(url):
    # Expressão regular para verificar se a URL contém apenas o ID do vídeo do YouTube
    padrao = r'^[A-Za-z0-9_-]{11}$'
    return re.match(padrao, url) is not None

def get_filtered_usernames(logged_in_user):
    queryset = AvaliacaoEficacia.objects.select_related('usuario')

    if logged_in_user.type == "LID":
        queryset = queryset.filter(avaliado_chefia=False)
    elif logged_in_user.type == "ADM":
        queryset = queryset.filter(avaliado_rh=False)
    
    usuario = queryset.values_list("usuario__first_name","usuario__last_name","usuario__matricula")

    nomes_usuarios = [f"{first_name} {last_name} - {matricula}" for first_name,last_name,matricula in usuario]

    return nomes_usuarios

@login_required
def pastas_add(request):
    if request.method == 'POST':
        form = AddPasta(request.POST)
        if form.is_valid():
            pasta = form.save(commit=False)
            pasta.created_by = request.user
            pasta.save()
            form.save_m2m()  # Salva os campos ManyToMany após salvar o objeto principal
            messages.success(request, 'Pasta adicionada com sucesso.')
            return redirect('list-pasta')
        
    return redirect('list-pasta')

@login_required
def pastas_list(request):
    form = AddPasta()
    setor_do_usuario_object = Funcionario.objects.select_related('setor').get(matricula=request.user.matricula)
    setor_do_usuario = setor_do_usuario_object.setor

    # Filtrando as pastas com base no tipo de usuário logado
    if request.user.type in ['ADM', 'DIR']:
        pastas = Pasta.objects.all().select_related('created_by').prefetch_related('setores', 'funcionarios').order_by("id")
    elif request.user.type == 'LID':
        pastas = Pasta.objects.filter(
            Q(created_by=request.user) |
            Q(setores=setor_do_usuario) |
            Q(funcionarios__matricula=request.user.matricula)
        ).distinct().select_related('created_by').prefetch_related('setores', 'funcionarios').order_by("id")
    else:
        pastas = Pasta.objects.filter(
            Q(setores=setor_do_usuario) |
            Q(funcionarios__matricula=request.user.matricula)
        ).distinct().select_related('created_by').prefetch_related('setores', 'funcionarios').order_by("id")

    # Obter as avaliações pendentes de forma otimizada
    if request.user.type == 'ADM':
        avaliacoes_pendentes = AvaliacaoEficacia.objects.filter(
            pasta__in=pastas,
            avaliado_rh=False
        ).values_list('pasta_id', flat=True)
    elif request.user.type == 'DIR':
        avaliacoes_pendentes = AvaliacaoEficacia.objects.filter(
            pasta__in=pastas,
            usuario__type = 'LID',
            avaliado_chefia=False
        ).values_list('pasta_id', flat=True)
    elif request.user.type == 'LID':
        avaliacoes_pendentes = AvaliacaoEficacia.objects.filter(
            pasta__in=pastas,
            usuario__type = 'LEI',
            avaliado_chefia=False,
            usuario__funcionario__setor = request.user.funcionario.setor
        ).values_list('pasta_id', flat=True)
    else:
        avaliacoes_pendentes = []

    # Transformar os IDs das pastas com avaliações pendentes em um set para acesso rápido
    pastas_com_avaliacao_pendente = set(avaliacoes_pendentes)

    # Pegar os nomes dos funcionários associados a cada pasta e verificar avaliações pendentes
    pastas_com_funcionarios = [
        {
            'pasta': pasta,
            'criador_nome_completo': f"{pasta.created_by.first_name} {pasta.created_by.last_name}",
            'possui_avaliacao_pendente': pasta.id in pastas_com_avaliacao_pendente,
        }
        for pasta in pastas
    ]

    return render(request, 'pastas/pasta_list.html', {
        'pastas_com_criadores': pastas_com_funcionarios,
        'form': form,
    })

@login_required
def funcionarios_avaliaram(request, pk):
    # Verifica se a requisição é do tipo AJAX (opcional)
    if request.method == 'GET' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Obtém a pasta usando o ID fornecido
        pasta = get_object_or_404(Pasta, id=pk)
        
        # Filtra as avaliações de eficácia relacionadas a essa pasta
        avaliacoes = AvaliacaoEficacia.objects.filter(pasta=pasta)

        if request.user.type == "ADM":
            usuarios_avaliados = list(avaliacoes.filter(avaliado_rh=False).values('usuario__first_name', 'usuario__last_name'))
        elif request.user.type == "LID":
            usuarios_avaliados = list(avaliacoes.filter(
                avaliado_chefia=False,
                usuario__type='LEI',
                usuario__funcionario__setor=request.user.funcionario.setor
            ).values('usuario__first_name', 'usuario__last_name'))
        else:
            usuarios_avaliados = list(avaliacoes.filter(avaliado_chefia=False, usuario__type='LID').values('usuario__first_name', 'usuario__last_name'))

        print(usuarios_avaliados)
        # Retorna uma JsonResponse com as informações
        return JsonResponse({
            'usuarios_avaliados': usuarios_avaliados
        })
    
    # Caso não seja uma requisição GET ou AJAX, retorna um erro 400
    return JsonResponse({'error': 'Requisição inválida'}, status=400)

@login_required
def pastas_detail(request, pk):
    pasta = get_object_or_404(Pasta, pk=pk)
    avaliacao_eficacia = AvaliacaoEficacia.objects.filter(pasta=pasta, usuario=request.user)
    resposta_avaliacao_eficacia = RespostaAvaliacaoEficacia.objects.filter(avaliacao_eficacia__in=avaliacao_eficacia)

    existe_avaliacao_eficacia = resposta_avaliacao_eficacia.exists()
    
    materiais = Material.objects.filter(pasta=pasta).order_by("id")

    print(materiais)

    visualizacoes = Visualizacao.objects.filter(
        funcionario__matricula=request.user.matricula,
        material__in=materiais
    ).values_list('material_id', flat=True)

    return render(request, 'pastas/pasta_detail.html', {
        'pasta': pasta,
        'materiais': materiais,
        'visualizacoes': visualizacoes,
        'existe_avaliacao_eficacia': existe_avaliacao_eficacia
    })

@login_required
def pasta_edit(request, pk):
    pasta = get_object_or_404(Pasta, pk=pk)
    if request.method == 'POST':
        form = AddPasta(request.POST, instance=pasta)
        if form.is_valid():
            pasta = form.save(commit=False)
            pasta.save()
            form.save_m2m()  # Salva os campos ManyToMany após salvar o objeto principal
            messages.success(request, 'Pasta editada com sucesso.')
            return redirect('detail-pasta',pk=pk)
    else:
        form = AddPasta(instance=pasta)
    return render(request, 'pastas/pasta_edit.html', {'form': form})

@login_required
def pasta_delete(request, pk):
    pasta = get_object_or_404(Pasta, pk=pk)
    pasta.delete()

    messages.success(request, 'Trilha excluída com sucesso.')

    return redirect('list-pasta')

@login_required
def material_add(request):
    if request.method == 'POST':
        form = AddMaterial(request.POST, request.FILES)
        if form.is_valid():
            material = form.save(commit=False)
            material.created_by = request.user

            # Extrair o ID do vídeo do YouTube com expressão regular:
            video_youtube_url = form.cleaned_data['video_youtube']
            if video_youtube_url:
                material.video_youtube = extrair_id_youtube(video_youtube_url)  # Chama a função

            material.save()
            return redirect('list-material')
    else:
        form = AddMaterial()
    return render(request, 'materiais/material_add.html', {'form': form})

@login_required
def material_add_in_pasta(request, pk):
    pasta = get_object_or_404(Pasta, pk=pk)

    if request.method == 'POST':
        form = AddMaterial(request.POST, request.FILES)
        if form.is_valid():
            material = form.save(commit=False)
            material.pasta = pasta  # Define a pasta associada
            material.created_by = request.user

            video_youtube_url = form.cleaned_data['video_youtube']
            print(video_youtube_url)
            if video_youtube_url and not is_id_youtube_valido(video_youtube_url):
                material.video_youtube = extrair_id_youtube(video_youtube_url)  # Chama a função

            material.save()
            form.save_m2m()
            return redirect('detail-pasta', pk=pasta.pk)
        
    else:
        form = AddMaterial()

    return render(request, 'materiais/material_add.html', {
        'form': form,
        'pasta': pasta
    })

@login_required
def material_list(request):
    materiais = Material.objects.all()
    return render(request, 'materiais/material_list.html', {
        'materiais': materiais
    })

@login_required
def material_detail(request, pk):
    material = get_object_or_404(Material, pk=pk)
    return render(request, 'materiais/material_detail.html', {
        'material': material
    })

@login_required
def material_edit(request, pk_material, pk_pasta):
    material = get_object_or_404(Material, pk=pk_material)
    pasta = get_object_or_404(Pasta, pk=pk_pasta)
    
    # Verificar se o material pertence à pasta
    if material.pasta != pasta:
        messages.error(request, 'Material não pertence à pasta especificada.')
        return redirect('detail-pasta', pk=pasta.pk)

    if request.method == 'POST':
        form = AddMaterial(request.POST, request.FILES, instance=material)
        if form.is_valid():
            material = form.save(commit=False)
            material.pasta = pasta  # Garante que a pasta está sendo corretamente atribuída

            video_youtube_url = form.cleaned_data['video_youtube']
            if video_youtube_url and not is_id_youtube_valido(video_youtube_url):  # Verifica se precisa formatar
                material.video_youtube = extrair_id_youtube(video_youtube_url)  # Chama a função
                
            material.save()
            form.save_m2m()  # Salva os campos ManyToMany após salvar o objeto principal
            messages.success(request, 'Material editado com sucesso.')
            return redirect('detail-pasta', pk=pasta.pk)
        else:
            messages.error(request, 'Erro ao editar o material. Verifique os dados informados.')
    else:
        form = AddMaterial(instance=material)
    
    return render(request, 'materiais/material_edit.html', {'form': form, 'material': material, 'pasta': pasta})

@login_required
def material_delete(request, pk_material, pk_pasta):
    pasta = get_object_or_404(Pasta,pk=pk_pasta)
    material = get_object_or_404(Material, pk=pk_material)
    material.delete()

    messages.success(request, 'Material excluído com sucesso.')

    return redirect('detail-pasta', pk=pasta.pk)

@login_required
def avaliacao(request, pk):
    if request.method == 'POST':
        # Capturando os valores do formulário
        valor_trabalho = request.POST.get('valor_trabalho')
        justificativa = request.POST.get('justificativa')

        # Convertendo para booleano
        eficacia_qualificacao = True if valor_trabalho == 'true' else False

        print(eficacia_qualificacao)

        # Obter a instância da pasta correspondente
        pasta = get_object_or_404(Pasta, id=pk)
        user = get_object_or_404(CustomUser, id=request.user.id)
        funcionario = get_object_or_404(Funcionario, matricula=user.matricula)
        setor = funcionario.setor

        lid = CustomUser.objects.filter(type='LID', matricula__in=Funcionario.objects.filter(setor=setor).values_list('matricula', flat=True)).first()

        trilha_nome = pasta.nome  # Nome da trilha

        # Enviar email ao LID informando sobre a trilha
        subject = f"Cemag Academy - Trilha {trilha_nome} foi finalizada e avaliada pelo colaborador {user.first_name} {user.last_name}"
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6;">
            <div style="max-width: 600px; margin: auto; border: 1px solid #ddd; border-radius: 10px; overflow: hidden; box-shadow: 0 0 10px rgba(0,0,0,0.1);">
                <div style="background-color: #ff7f27; padding: 20px; text-align: center; color: white;">
                    <h1>Trilha Avaliada!</h1>
                </div>
                <div style="padding: 20px;">
                    <p style="font-size: 16px;">Olá,</p>
                    <p style="font-size: 16px;">A trilha <strong>'{trilha_nome}'</strong> foi avaliada com sucesso pelo colaborador <strong>{user.first_name} {user.last_name}</strong>.</p>
                    
                    <table style="width: 100%; margin-top: 20px; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 10px; border: 1px solid #ddd; background-color: #f9f9f9; font-weight: bold;">A qualificação agregará valor para o seu trabalho:</td>
                            <td style="padding: 10px; border: 1px solid #ddd; background-color: #f9f9f9; color: {'green' if eficacia_qualificacao else 'red'};">
                                {'Sim' if eficacia_qualificacao else 'Não'}
                            </td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; border: 1px solid #ddd; background-color: #f9f9f9; font-weight: bold;">Justificativa:</td>
                            <td style="padding: 10px; border: 1px solid #ddd; background-color: #f9f9f9;">{justificativa}</td>
                        </tr>
                    </table>
                    
                    <p style="font-size: 16px; margin-top: 20px;">Agora você poderá avaliar o colaborador na aba de Trilhas.</p>
                    <p style="font-size: 16px; margin-top: 20px;">Se precisar de mais informações, não hesite em entrar em contato.</p>
                    <p style="font-size: 16px;">Atenciosamente,<br>Equipe de Treinamento</p>
                    
                    <div style="text-align: center; margin-top: 30px;">
                        <a href="https://cemag-academy.onrender.com/materiais/pasta/" style="padding: 10px 20px; background-color: #ff7f27; color: white; text-decoration: none; border-radius: 5px;">Acesse nosso site para avaliar o colaborador</a>
                    </div>
                </div>
                <div style="background-color: #f1f1f1; padding: 10px; text-align: center; color: #555;">
                    <p>Este é um e-mail automático. Por favor, não responda.</p>
                </div>
            </div>
        </body>
        </html>
        """
        if lid and user.type != 'LID':
            if lid.email:
                print("ENTROU AQUI")
                # Cria um objeto EmailMultiAlternatives para o LID
                email_lid = EmailMultiAlternatives(
                    subject,
                    "Este é um email em texto simples.",
                    settings.DEFAULT_FROM_EMAIL,
                    [lid.email],
                )
                email_lid.attach_alternative(html_content, "text/html")  # Adiciona o conteúdo HTML
                email_lid.send(fail_silently=False)
            else: 
                print(f"{lid.first_name} não possui email cadastrado")
        else:
            print("O LÍDER fez a avaliação ou esse setor não possui LÍDER cadastrado")
        
        # Enviar email para todos os usuários do tipo ADM
        adm_users = CustomUser.objects.filter(type='ADM')
        for adm in adm_users:
            # Cria o email para cada ADM
            if adm.email:
                email_adm = EmailMultiAlternatives(
                    subject,
                    "Este é um email em texto simples.",
                    settings.DEFAULT_FROM_EMAIL,
                    [adm.email],
                )
                email_adm.attach_alternative(html_content, "text/html")  # Adiciona o conteúdo HTML
                email_adm.send(fail_silently=False)
            else:
                print(f"{adm.first_name} não possui um email cadastrado")

        # Verificar se já existe uma avaliação para esse usuário e essa pasta
        avaliacao_eficacia, created = AvaliacaoEficacia.objects.get_or_create(
            pasta=pasta,
            usuario=request.user
        )

        # Marcar como avaliado pela chefia ou RH, dependendo do tipo de usuário
        if request.user.type == 'ADM':
            avaliacao_eficacia.avaliado_rh = True
            avaliacao_eficacia.avaliado_chefia = True
        
        avaliacao_eficacia.save()

        # Criar a resposta da avaliação
        RespostaAvaliacaoEficacia.objects.create(
            avaliacao_eficacia=avaliacao_eficacia,
            eficacia_qualificacao=eficacia_qualificacao,
            justificativa_qualificacao=justificativa,
            usuario=request.user
        )

        # Redirecionar após o processamento
        return redirect('detail-pasta', pk=pk)

    return redirect('detail-pasta', pk=pk)

@login_required
def avaliacao_chefia(request, pk):

    if request.method == 'GET':
        colaborador = request.GET.get('collaborator')
        
        # O 'pk' é o identificador da pasta que você passou na URL
        pasta = get_object_or_404(Pasta, id=pk)

        # Recupere o funcionário com base no nome
        funcionario = Funcionario.objects.get(nome=colaborador)
        usuario = CustomUser.objects.get(matricula=funcionario.matricula)

        # Verificar se já existe uma avaliação para esse usuário e essa pasta
        avaliacao_eficacia = AvaliacaoEficacia.objects.get(
            pasta=pasta,
            usuario__matricula=funcionario.matricula
        )

        resposta_avaliacao = RespostaAvaliacaoEficacia.objects.get(
            avaliacao_eficacia=avaliacao_eficacia,
            usuario=usuario
        )

        # Retorna os dados via JSON
        return JsonResponse({
            'resposta': resposta_avaliacao.justificativa_qualificacao,
            'qualificacao': resposta_avaliacao.eficacia_qualificacao
        })
    
    elif request.method == 'POST':

        eficacia_qualificacao = request.POST.get('eficacia_qualificacao')
        justificativa_qualificacao = request.POST.get('justificativa_qualificacao')
        colaborador = request.POST.get('filter_collaborator')
        filtrar_funcionário = False 

        eficacia_qualificacao = True if eficacia_qualificacao == "on" else False

        pasta = get_object_or_404(Pasta, id=pk)

        # Recupere o funcionário com base no nome
        try:
            funcionario = Funcionario.objects.get(nome=colaborador)
            avaliacao_eficacia = AvaliacaoEficacia.objects.get(
            pasta=pasta,
            usuario__matricula=funcionario.matricula
        )
        except Funcionario.DoesNotExist:
            avaliacao_eficacia = AvaliacaoEficacia.objects.get(
                pasta=pasta,
                usuario__matricula=colaborador
            )
            filtrar_funcionário = True


        if request.user.type == "ADM":
            avaliacao_eficacia.avaliado_rh = True
        else:
            avaliacao_eficacia.avaliado_chefia = True
        
        avaliacao_eficacia.save()

        resposta_avaliacao = RespostaAvaliacaoEficacia.objects.create(
            avaliacao_eficacia=avaliacao_eficacia,
            eficacia_qualificacao=eficacia_qualificacao,
            justificativa_qualificacao=justificativa_qualificacao,
            usuario=request.user
        )
        if filtrar_funcionário:
            return redirect('jornada_detail')
        
        return redirect('list-pasta')

@login_required
def jornada_detail(request):
    # Caso não seja uma requisição AJAX, renderiza a página com os funcionários iniciais
    if request.user.type == 'ADM':
        funcionarios_iniciais = Funcionario.objects.all().order_by('nome')

        return render(request, 'jornada/jornada_funcionario.html', {
            'funcionarios_iniciais': funcionarios_iniciais
        })
    else:
        return redirect('home')

@login_required
def jornada_detail_unique(request,matricula):

    try:
        funcionario = Funcionario.objects.get(matricula=matricula)
        usuario = CustomUser.objects.get(matricula=matricula)
    except Funcionario.DoesNotExist:
        # Se o funcionário não existir, retorne um erro
        return JsonResponse({'error': 'Funcionário não encontrado'}, status=404)
    except CustomUser.DoesNotExist:
        # Se o usuário não existir, retorne um erro
        return JsonResponse({'error': 'Usuário não encontrado'}, status=404)
    
    # Enviando dados dos "Cursos finalizados"
    visualizacoes = Visualizacao.objects.filter(funcionario=funcionario)
    materiais_visualizados = [f"{visualizacao.pasta.nome} - {visualizacao.material.nome}" for visualizacao in visualizacoes]

    provas_realizadas = ProvaRealizada.objects.filter(usuario=usuario)

    livros_visualizados = VisualizacaoLivro.objects.filter(user=usuario)

    lista_provas_realizadas = []

    for prova_realizada in provas_realizadas:
        total_respostas, total_questoes = calcular_nota(prova_realizada.prova,usuario)  # Chama a função calcular_nota
        nota_final = (total_respostas/total_questoes) * 10 if total_questoes > 0 else 0
        nota_final = round(nota_final,2)
        lista_provas_realizadas.append({
            'id': prova_realizada.prova.id,
            'prova_titulo': prova_realizada.prova.titulo,
            'data_realizacao': prova_realizada.data_realizacao.strftime('%d/%m/%Y %H:%M:%S'),
            'nota_final': nota_final  # Adiciona a nota total calculada
        })

    lista_livros_visualizados = []

    for livro_visualizado in livros_visualizados:
        try:
            rating = Rating.objects.get(user=usuario,livro=livro_visualizado.livro)
        except Rating.DoesNotExist:
            rating = None
        lista_livros_visualizados.append({
            'livro_titulo': livro_visualizado.livro.titulo,
            'rating':rating.score if rating else 0
        })

    setor_do_usuario = funcionario.setor

    pastas = Pasta.objects.filter(
        Q(setores=setor_do_usuario) |
        Q(funcionarios__matricula=matricula)
    ).distinct()

    # Corrigindo para usar __in com a lista de pastas
    provas = Prova.objects.filter(pasta__in=pastas)

    dados_certificado = validacao_certificado(provas,usuario)

    pastas_certificadas = dados_certificado[0]

    dict_avaliacao_eficacia = {}
    lista_id = []
    lista_trilhas = []
    lista_avaliacoes_supervisor = []
    lista_avaliacoes_rh = []

    for pasta in pastas:
        get_pasta = get_object_or_404(Pasta, id=pasta.id)
        # Verificar se já existe uma avaliação para esse usuário e essa pasta
        try:
            avaliacao_eficacia = AvaliacaoEficacia.objects.get(
                pasta=get_pasta,
                usuario__matricula=funcionario.matricula
            )
            lista_id.append(avaliacao_eficacia.id)
            lista_trilhas.append(avaliacao_eficacia.pasta.nome)
            lista_avaliacoes_supervisor.append(avaliacao_eficacia.avaliado_chefia)
            lista_avaliacoes_rh.append(avaliacao_eficacia.avaliado_rh)
        except AvaliacaoEficacia.DoesNotExist:
            avaliacao_eficacia = None
        
    dict_avaliacao_eficacia['avaliacoes_id'] = lista_id
    dict_avaliacao_eficacia['trilhas'] = lista_trilhas
    dict_avaliacao_eficacia['avaliacoes_supervisor'] = lista_avaliacoes_supervisor
    dict_avaliacao_eficacia['avaliacoes_rh'] = lista_avaliacoes_rh
        
    return JsonResponse({
        'lista_materiais_visualizados':materiais_visualizados,
        'lista_provas_realizadas':lista_provas_realizadas,
        'lista_livros_visualizados':lista_livros_visualizados,
        'pastas_certificadas':pastas_certificadas,
        'dict_avaliacao_eficacia':dict_avaliacao_eficacia
    })

@login_required
def respostas_avaliacao(request, pk_avaliacao):

    # Obter a avaliação específica pelo ID
    avaliacao_eficacia = AvaliacaoEficacia.objects.get(id=pk_avaliacao)

    # Filtrar as respostas relacionadas a essa avaliação
    resposta_avaliacao = RespostaAvaliacaoEficacia.objects.filter(avaliacao_eficacia=avaliacao_eficacia)
    avaliacao_usuario_pesquisado = resposta_avaliacao.filter(usuario__type=avaliacao_eficacia.usuario.type).first()
    type_user = 'DIR' if avaliacao_eficacia.usuario.type == 'LID' else 'LID'
    resposta_lid = resposta_avaliacao.filter(usuario__type=type_user).first()
    resposta_adm = resposta_avaliacao.filter(usuario__type='ADM').first()

    # Enviar os dados da avaliação e das respostas para o template
    return render(request, 'pastas/avaliacao/avaliacao.html', {
        'avaliacao_eficacia': avaliacao_eficacia,
        'avaliacao_usuario_pesquisado':avaliacao_usuario_pesquisado,
        'resposta_lid':resposta_lid,
        'resposta_adm':resposta_adm
    })

@login_required
def registrar_visualizacao(request):
    if request.method == 'POST':
        material_id = request.POST.get('material_id')
        pasta_id = request.POST.get('pasta_id')

        try:
            funcionario = get_object_or_404(Funcionario, matricula=request.user.matricula)
            pasta = get_object_or_404(Pasta, id=pasta_id)
            material = get_object_or_404(Material, id=material_id)

            visualizacao = Visualizacao.objects.get(
                funcionario=funcionario,  # Use o objeto Funcionario
                pasta=pasta,             # Use o objeto Pasta
                material=material        # Use o objeto Material
            )

            visualizacao.delete()
            return JsonResponse({'status': 'desmarcado'})

        except Visualizacao.DoesNotExist:
            visualizacao = Visualizacao(
                funcionario=funcionario, 
                pasta=pasta, 
                material=material 
            )
            visualizacao.save()
            return JsonResponse({'status': 'marcado'})

@login_required
def gerar_ficha_frequencia(request, pk):
    pasta = get_object_or_404(Pasta, pk=pk)  # Busca a pasta pelo ID

    total_materiais = Material.objects.filter(pasta=pasta).count()

    # Subquery para calcular a contagem de materiais visualizados por funcionário
    visualizacoes_por_funcionario = (
        Visualizacao.objects
        .filter(pasta=pasta)
        .values('funcionario','visualizado_em')
        .annotate(total_visualizados=Count('material'))
        .filter(total_visualizados=total_materiais)
    )

    funcionario_ids = [v['funcionario'] for v in visualizacoes_por_funcionario]

    funcionarios = Funcionario.objects.filter(id__in=funcionario_ids)

    # Lógica para gerar o PDF (utilizando reportlab ou outra biblioteca)
    template = get_template('frequencia/ficha_frequencia.html')  # Carrega o template HTML
    context = {'funcionarios': funcionarios, 'pasta': pasta, 'visualizacoes_por_funcionario': visualizacoes_por_funcionario}  # Passa os dados para o template
    html = template.render(context)  # Renderiza o HTML

    # Converte o HTML renderizado em PDF
    pdf = BytesIO()
    pisa.CreatePDF(BytesIO(html.encode('UTF-8')), dest=pdf)  # Converte HTML para PDF

    # Configuração da resposta HTTP
    response = HttpResponse(pdf.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="ficha_frequencia_{pasta.nome}.pdf"'

    return response

@login_required
def list_participantes(request, pk):
    
    # Obtém a prova e a pasta relacionada
    prova = get_object_or_404(Prova, pk=pk)
    pasta = prova.pasta
    
    # Obtém os setores e funcionários relacionados à pasta
    setores = pasta.setores.all()
    funcionarios = pasta.funcionarios.all()
    
    # Listar participantes usando o setor
    # participantes_setor = Funcionario.objects.filter(setor__in=setores)

    # Combinar os participantes e remover duplicados
    list_participantes = set()
    
    for participante in funcionarios:
        list_participantes.add(participante)
    
    # Convertendo o conjunto de volta para uma lista
    list_participantes = list(list_participantes)
    
    # Obter as matrículas dos participantes
    matriculas = [participante.matricula for participante in list_participantes]
    
    # Obter os usuários correspondentes no CustomUser
    usuarios = CustomUser.objects.filter(matricula__in=matriculas)

    # Criar um dicionário para mapear funcionários a usuários
    funcionarios_para_usuarios = {user.matricula: user for user in usuarios}
    
    # Filtrar ProvaRealizada usando os usuários e a prova
    prova_realizada = ProvaRealizada.objects.filter(usuario__in=usuarios, prova=prova)
    
    # Criar um dicionário para armazenar se cada participante realizou a prova
    participantes_status = {participante.matricula: False for participante in list_participantes}
    
    # Atualizar o dicionário com os participantes que realizaram a prova
    for realizacao in prova_realizada:
        participantes_status[realizacao.usuario.matricula] = True
    
    # Criar uma lista final com os dados dos participantes, o status da prova e a nota
    lista_final_participantes = []
    for participante in list_participantes:
        usuario = funcionarios_para_usuarios.get(participante.matricula)
        
        # Calcular a nota e o número total de questões para o participante usando o usuário correspondente
        if usuario:
            total_respostas, total_questoes = calcular_nota(prova, usuario)
        else:
            total_respostas, total_questoes = 0, 0

        # Calcular a porcentagem de acertos (se não houver questões, definir como 0%)
        porcentagem_acertos = (total_respostas / total_questoes * 100) if total_questoes > 0 else 0

        # Adicionar o participante e os detalhes à lista final
        lista_final_participantes.append({
            'matricula': participante.matricula,
            'nome': participante.nome,
            'realizou_prova': participantes_status[participante.matricula],
            'nota': total_respostas,  # Nota total obtida pelo participante
            'total_questoes': total_questoes,  # Total de questões na prova
            'porcentagem_acertos': f'{porcentagem_acertos:.2f}%'  # Porcentagem de acertos formatada
        })
    
    return render(request, 'pastas/participantes_list.html', {
        'lista_participantes': lista_final_participantes,
        'prova': prova
    })

@login_required
def gerar_certificado(request):
    
    if request.method == 'POST':
        pasta_id = request.POST.get('pasta_id')
        matricula = request.POST.get('matricula')

        funcionario = get_object_or_404(Funcionario, matricula=matricula)
        usuario = get_object_or_404(CustomUser, matricula=matricula)

        # Verificar se já existe um Certificado para esse usuário e pasta
        certificado = Certificado.objects.filter(pasta_id=pasta_id, usuario=usuario).first()
        if not certificado:
            # Criar um novo certificado
            pasta = get_object_or_404(Pasta, pk=pasta_id)
            certificado = Certificado.objects.create(pasta=pasta, usuario=usuario)

        # Obter materiais da pasta
        materiais = Material.objects.filter(pasta_id=pasta_id)
                
        context = {'funcionario':funcionario,
                'materiais':materiais,
                'certificado':certificado}

        return render(request, 'certificados/certificado1.html', context=context)

@login_required
def consultar_certificado(request, uuid):
    if uuid:
        try:
            # Consulta o certificado e os dados relacionados
            certificado = Certificado.objects.filter(identificador_finalizado=uuid).first()
            if not certificado:
                return JsonResponse({'error': 'Certificado não encontrado. Verifique o código inserido e tente novamente'}, status=404)

            funcionario = get_object_or_404(Funcionario, matricula=certificado.usuario.matricula)
            materiais = Material.objects.filter(pasta_id=certificado.pasta)

            # Contexto a ser passado para o template
            context = {'funcionario': funcionario, 'materiais': materiais, 'certificado': certificado}

            # Renderiza a página `certificado1.html` com o contexto
            return render(request, 'certificados/certificado1.html', context=context)
        except Exception as e:
            print(e)
            # Retorna um JsonResponse com a mensagem de erro em caso de exceção
            return JsonResponse({'error': 'Certificado não encontrado. Verifique o código inserido e tente novamente'}, status=404)
    else:
        # Retorna um JsonResponse com mensagem de erro para UUID inválido
        return JsonResponse({'error': 'Por favor, forneça um UUID válido.'}, status=400)
