from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.urls import reverse

from .models import Pasta, ArquivosDrive
from .utils import Drive
from .views import pasta_edit


@login_required
def pasta_edit_drive(request, pk):
    """
    Atualiza os registros de ArquivosDrive da pasta com base
    nos arquivos selecionados na edição, e em seguida delega
    para a view original de edição de pasta.
    """
    if request.method == 'POST':
        pasta = get_object_or_404(Pasta, pk=pk)

        arquivos_ids = request.POST.getlist('arquivos_drive_ids')
        ArquivosDrive.objects.filter(pasta=pasta).delete()
        for arquivo_id in arquivos_ids:
            if arquivo_id:
                ArquivosDrive.objects.create(pasta=pasta, id_arquivo=arquivo_id)

    return pasta_edit(request, pk)


@login_required
def pastas_detail_drive_filtrado(request, pk):
    """
    Retorna os arquivos do Drive da pasta.
    - Se houver registros em ArquivosDrive para a pasta, mostra apenas esses arquivos.
    - Se não houver, mostra todos os arquivos da pasta do Drive.
    """
    pasta = get_object_or_404(Pasta, pk=pk)
    drive = Drive()

    if not pasta.pasta_drive:
        return JsonResponse({
            'success': False,
            'error': 'Pasta do Drive não configurada',
            'arquivos': []
        })

    drive_id = drive.extrair_id_drive(pasta.pasta_drive)

    can_clear_cache = (request.user.type == "ADM" or
                       request.user.id == pasta.created_by.id)

    if not drive_id:
        return JsonResponse({
            'success': False,
            'error': f'ID do Drive inválido: {pasta.pasta_drive}',
            'arquivos': []
        })

    # IDs de arquivos selecionados para esta pasta (se existirem)
    arquivos_selecionados_ids = list(
        ArquivosDrive.objects.filter(pasta=pasta).values_list('id_arquivo', flat=True)
    )
    filtrar_por_selecionados = len(arquivos_selecionados_ids) > 0

    # Obtém arquivos do Drive usando o ID extraído
    arquivos_drive = drive.listar_arquivos_pasta(drive_id)

    # Processa os arquivos...
    arquivos_processados = []
    for arquivo in arquivos_drive:
        # O 'id' do arquivo é essencial
        file_id = arquivo.get('id')
        if not file_id:
            continue  # Pula arquivos sem ID

        # Se houver arquivos selecionados para a pasta,
        # mostra apenas esses; caso não haja, mostra todos.
        if filtrar_por_selecionados and file_id not in arquivos_selecionados_ids:
            continue

        arquivo_data = {
            'id': file_id,
            'nome': arquivo.get('name'),
            'tipo': arquivo.get('mimeType'),
            'extensao': arquivo.get('fileExtension'),
            'link_visualizacao': reverse('download_drive_file', args=[file_id]),
            'link_download': reverse('download_drive_file', args=[file_id]),
            'thumbnail': arquivo.get('thumbnailLink'),
            'modificado': arquivo.get('modifiedTime'),
            'tamanho_bytes': arquivo.get('size'),
            'tamanho': drive.formatar_tamanho_arquivo(arquivo.get('size')),
            'icone': drive.obter_icone_por_tipo(arquivo.get('mimeType')),
            'can_clear_cache': can_clear_cache,
        }

        arquivos_processados.append(arquivo_data)

    arquivos_processados.sort(key=lambda x: x['nome'].lower())

    return JsonResponse({
        'success': True,
        'can_clear_cache_pasta': can_clear_cache,
        'pasta_id': pasta.id,
        'pasta_nome': pasta.nome,
        'total_arquivos': len(arquivos_processados),
        'arquivos': arquivos_processados
    })

