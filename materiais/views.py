from django.shortcuts import render, redirect,get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.db.models import Count, Q
from django.http import HttpResponse
from django.template.loader import get_template
from django.conf import settings  # Importe o módulo settings

from .models import Pasta,Material,Visualizacao,AvaliacaoEficacia, RespostaAvaliacaoEficacia
from avaliacoes.views import calcular_nota,validacao_certificado
from .forms import AddPasta,AddMaterial,VisualizacaoForm
from cadastros.models import Funcionario,Setor
from biblioteca.models import VisualizacaoLivro
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
    # Filtrando as pastas com base no tipo de usuário logado
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

    # Pegar os nomes dos funcionários associados a cada pasta
    pastas_com_funcionarios = []
    for pasta in pastas:
        funcionario_associados = pasta.funcionarios.all()

        setores_associados = pasta.setores.all()
        funcionario_dos_setores = Funcionario.objects.filter(setor__in=setores_associados)

        todos_funcionarios = funcionario_associados | funcionario_dos_setores
        todos_funcionarios = todos_funcionarios.distinct()

        nomes_funcionarios = []

        criador = CustomUser.objects.get(id=pasta.created_by_id)
        criador_nome_completo = f"{criador.first_name} {criador.last_name}"
        
        for funcionario in todos_funcionarios:
            try:
                usuario = CustomUser.objects.get(matricula=funcionario.matricula)
                queryset = AvaliacaoEficacia.objects.filter(usuario=usuario)
                if request.user.type == "LID":
                    queryset = queryset.filter(avaliado_chefia=False)

                # Caso o tipo de usuário seja 'ADM', pegar avaliações ainda não avaliadas pelo RH (avaliado_rh=False)
                elif request.user.type == "ADM":
                    queryset = queryset.filter(avaliado_rh=False)

                # Verificar se há avaliações para esse funcionário que atendam ao critério
                if queryset.exists():
                    nome_completo = f"{funcionario.nome}"
                    nomes_funcionarios.append(nome_completo)
            except CustomUser.DoesNotExist:
                pass  # Se o usuário não for encontrado, pode ignorar ou lidar com isso como preferir

        pastas_com_funcionarios.append({
            'pasta': pasta,
            'criador_nome_completo': criador_nome_completo,
            'nomes_funcionarios': nomes_funcionarios,
        })


    return render(request, 'pastas/pasta_list.html', {
        'pastas_com_criadores': pastas_com_funcionarios,
        'form': form,
    })

@login_required
def pastas_detail(request, pk):
    pasta = get_object_or_404(Pasta, pk=pk)
    avaliacao_eficacia = AvaliacaoEficacia.objects.filter(pasta=pasta, usuario=request.user)
    resposta_avaliacao_eficacia = RespostaAvaliacaoEficacia.objects.filter(avaliacao_eficacia__in=avaliacao_eficacia)

    existe_avaliacao_eficacia = resposta_avaliacao_eficacia.exists()
    
    materiais = Material.objects.filter(pasta=pasta)

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
def avaliacao(request, pk):
    if request.method == 'POST':
        # Capturando os valores do formulário
        valor_trabalho = request.POST.get('valor_trabalho')
        justificativa = request.POST.get('justificativa')

        # Convertendo para booleano
        eficacia_qualificacao = True if valor_trabalho == 'true' else False

        # Obter a instância da pasta correspondente
        pasta = get_object_or_404(Pasta, id=pk)

        # Verificar se já existe uma avaliação para esse usuário e essa pasta
        avaliacao_eficacia, created = AvaliacaoEficacia.objects.get_or_create(
            pasta=pasta,
            usuario=request.user
        )

        # Marcar como avaliado pela chefia ou RH, dependendo do tipo de usuário
        if request.user.type == 'LID':
            avaliacao_eficacia.avaliado_chefia = True
        elif request.user.type == 'ADM':
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
        nome_colaborador = request.POST.get('filter_collaborator')

        eficacia_qualificacao = True if eficacia_qualificacao == "on" else False

        pasta = get_object_or_404(Pasta, id=pk)

        # Recupere o funcionário com base no nome
        funcionario = Funcionario.objects.get(nome=nome_colaborador)

        avaliacao_eficacia = AvaliacaoEficacia.objects.get(
            pasta=pasta,
            usuario__matricula=funcionario.matricula
        )

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

        return redirect('list-pasta')

@login_required
def jornada_detail(request):
    # Caso não seja uma requisição AJAX, renderiza a página com os funcionários iniciais
    funcionarios_iniciais = Funcionario.objects.all().order_by('nome')

    return render(request, 'jornada/jornada_funcionario.html', {
        'funcionarios_iniciais': funcionarios_iniciais
    })

@login_required
def jornada_detail_unique(request,matricula):

    try:
        funcionario = Funcionario.objects.get(matricula=matricula)
        usuario = CustomUser.objects.get(matricula=matricula)
    except Funcionario.DoesNotExist:
        # Se o funcionário não existir, retorne um erro
        return JsonResponse({'error': 'Funcionário não encontrado'}, status=404)
    
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
            'prova_titulo': prova_realizada.prova.titulo,
            'data_realizacao': prova_realizada.data_realizacao.strftime('%d/%m/%Y %H:%M:%S'),
            'nota_final': nota_final  # Adiciona a nota total calculada
        })

    lista_livros_visualizados = []

    for livro_visualizado in livros_visualizados:
        lista_livros_visualizados.append({
            'livro_titulo': livro_visualizado.livro.titulo,
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
    resposta_adm = resposta_avaliacao.filter(usuario__type='ADM').first()
    
    if resposta_adm.eficacia_qualificacao:
        print(resposta_adm.eficacia_qualificacao)
    else:
        print(resposta_adm.eficacia_qualificacao)

    # Enviar os dados da avaliação e das respostas para o template
    return render(request, 'pastas/avaliacao/avaliacao.html', {
        'avaliacao_eficacia': avaliacao_eficacia,
        'resposta_avaliacao': resposta_avaliacao,
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
@login_required
def gerar_certificado(request):
    
    if request.method == 'POST':

        prova_id = request.POST.get('prova_id')
        pasta_id = request.POST.get('pasta_id')
        matricula = request.POST.get('matricula')

        prova = get_object_or_404(Prova, pk=prova_id)
        
        # prova_realizada = get_object_or_404(ProvaRealizada, usuario=request.user, prova=prova)
            
        funcionario = get_object_or_404(Funcionario, matricula=matricula)

        materiais = Material.objects.filter(pasta_id=pasta_id)
                
        context = {'funcionario':funcionario,
                'prova':prova,
                'materiais':materiais}

        return render(request, 'certificados/certificado1.html', context=context)