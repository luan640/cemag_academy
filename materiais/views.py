from django.shortcuts import render, redirect,get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.db.models import Count, Q
from django.http import HttpResponse
from django.template.loader import get_template
from django.conf import settings  # Importe o módulo settings

from .models import Pasta,Material,Visualizacao
from .forms import AddPasta,AddMaterial,VisualizacaoForm
from cadastros.models import Funcionario,Setor
from avaliacoes.models import ProvaRealizada, Prova
from users.models import CustomUser

from reportlab.pdfgen import canvas
import re
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
    if request.user.type == 'ADM':
        pastas = Pasta.objects.all()
    elif request.user.type == 'LID':
        setor_do_usuario_object = Funcionario.objects.get(matricula=request.user.matricula)
        setor_do_usuario = setor_do_usuario_object.setor
        pastas = Pasta.objects.filter(
            Q(created_by=request.user) |
            Q(setores=setor_do_usuario) |
            Q(funcionarios__matricula=request.user.matricula)
        ).distinct()
    else:
        setor_do_usuario_object = Funcionario.objects.get(matricula=request.user.matricula)
        setor_do_usuario = setor_do_usuario_object.setor
        pastas = Pasta.objects.filter(
            Q(setores=setor_do_usuario) |
            Q(funcionarios__matricula=request.user.matricula)
        ).distinct()

    # Pegar os nomes dos criadores das pastas
    pastas_com_criadores = []
    for pasta in pastas:
        criador = CustomUser.objects.get(id=pasta.created_by_id)
        criador_nome_completo = f"{criador.first_name} {criador.last_name}"
        pastas_com_criadores.append({
            'pasta': pasta,
            'criador_nome_completo': criador_nome_completo
        })

    return render(request, 'pastas/pasta_list.html', {'pastas_com_criadores': pastas_com_criadores, 'form': form})

@login_required
def pastas_detail(request, pk):
    pasta = get_object_or_404(Pasta, pk=pk)
    materiais = Material.objects.filter(pasta=pasta)

    visualizacoes = Visualizacao.objects.filter(
        funcionario__matricula=request.user.matricula,
        material__in=materiais
    ).values_list('material_id', flat=True)

    return render(request, 'pastas/pasta_detail.html', {
        'pasta': pasta,
        'materiais': materiais,
        'visualizacoes': visualizacoes,
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
            return redirect('list-pasta')
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
            if video_youtube_url:
                material.video_youtube = extrair_id_youtube(video_youtube_url)  # Chama a função

            material.save()
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
def jornada_detail(request,pk_user=None):
    
    if request.method == 'POST':
        funcionario = get_object_or_404(Funcionario, pk=pk_user)

    return render(request, 'jornada/jornada_funcionario.html', {
    })

@login_required
def jornada_detail_unique(request):

    return render(request, 'jornada/jornada_funcionario.html', {"dict"})

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

def list_participantes(request, pk):
    
    # Obtém a prova e a pasta relacionada
    prova = get_object_or_404(Prova, pk=pk)
    pasta = prova.pasta
    
    # Obtém os setores e funcionários relacionados à pasta
    setores = pasta.setores.all()
    funcionarios = pasta.funcionarios.all()
    
    # Listar participantes usando o setor
    setor_participantes = Funcionario.objects.filter(setor__in=setores)

    # Combinar os participantes e remover duplicados
    list_participantes = set()
    
    for participante in setor_participantes:
        list_participantes.add(participante)
    
    for participante in funcionarios:
        list_participantes.add(participante)
    
    # Convertendo o conjunto de volta para uma lista
    list_participantes = list(list_participantes)
    
    # Obter as matrículas dos participantes
    matriculas = [participante.matricula for participante in list_participantes]
    
    # Obter os usuários correspondentes no CustomUser
    usuarios = CustomUser.objects.filter(matricula__in=matriculas)
    
    # Filtrar ProvaRealizada usando os usuários e a prova
    prova_realizada = ProvaRealizada.objects.filter(usuario__in=usuarios, prova=prova)
    
    # Criar um dicionário para armazenar se cada participante realizou a prova
    participantes_status = {participante.matricula: False for participante in list_participantes}
    
    # Atualizar o dicionário com os participantes que realizaram a prova
    for realizacao in prova_realizada:
        participantes_status[realizacao.usuario.matricula] = True
    
    # Criar uma lista final com os dados dos participantes e o status da prova
    lista_final_participantes = []
    for participante in list_participantes:
        lista_final_participantes.append({
            'matricula': participante.matricula,
            'nome': participante.nome,
            'realizou_prova': participantes_status[participante.matricula]
        })
    

    return render(request, 'pastas/participantes_list.html', {'lista_participantes':lista_final_participantes, 'prova':prova})

# def gerar_certificado(request, pk):
    
#     template = get_template('certificados/certificado1.html')  # Carrega o template HTML
#     context = {'teste':'teste'}  # Passa os dados para o template
#     html = template.render(context)  # Renderiza o HTML

#     # Converte o HTML renderizado em PDF
#     pdf = BytesIO()
#     pisa.CreatePDF(BytesIO(html.encode('UTF-8')), dest=pdf)  # Converte HTML para PDF

#     # Configuração da resposta HTTP
#     response = HttpResponse(pdf.getvalue(), content_type='application/pdf')
#     response['Content-Disposition'] = f'attachment; filename="certificado_.pdf"'


#     return response
    
#     # return render(request, "certificados/certificado1.html")
def gerar_certificado(request, pk, pk_pasta):
    
    prova = get_object_or_404(Prova, pk=pk)
    
    prova_realizada = get_object_or_404(ProvaRealizada, usuario=request.user, prova=prova)
        
    funcionario = get_object_or_404(Funcionario, matricula=request.user.matricula)

    materiais = Material.objects.filter(pasta_id=pk_pasta)
            
    context = {'funcionario':funcionario,
               'prova':prova,
               'dados_prova':prova_realizada,
               'materiais':materiais}

    return render(request, 'certificados/certificado1.html', context=context)