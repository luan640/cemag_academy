document.addEventListener('DOMContentLoaded', function() {
    const listaMateriais = document.getElementById('lista-materiais');
    const hasDrive = listaMateriais.getAttribute('data-has-drive') === 'true';
    const pastaId = listaMateriais.getAttribute('data-pasta-id');
    
    if (hasDrive && pastaId) {
        carregarArquivosDrive(pastaId);
    }
});
function carregarArquivosDrive(pastaId) {
    const loadingElement = document.getElementById('drive-loading');
    const driveContent = document.getElementById('drive-content');
    
    fetch(`/materiais/pasta/${pastaId}/drive/`)
        .then(response => response.json())
        .then(data => {
            if (data.success && data.arquivos.length > 0) {
                driveContent.innerHTML = renderizarArquivosDrive(data.arquivos);
            } else {
                driveContent.innerHTML = renderizarMensagemVaziaDrive(
                    data.error || 'Nenhum arquivo encontrado no Drive'
                );
            }
        })
        .catch(error => {
            driveContent.innerHTML = renderizarErroDrive('Erro ao carregar arquivos do Drive');
            console.error('Erro:', error);
        });
}

function renderizarArquivosDrive(arquivos) {
    let html = '<div class="list-group">';
    
    arquivos.forEach(arquivo => {
        html += `
        <div class="list-group-item list-group-item-action flex-column align-items-start drive-item">
            <div class="d-flex w-100 justify-content-between align-items-center">
                <div class="d-flex align-items-center" style="gap: 15px;">
                    <i class="fa-regular ${arquivo.icone} fa-2x text-success"></i>
                    <div class="flex-grow-1">
                        <h6 class="mb-1">${arquivo.nome}</h6>
                        <small class="text-muted">
                            ${arquivo.tamanho} • 
                            ${arquivo.modificado ? 'Modificado recentemente' : ''}
                        </small>
                    </div>
                </div>
                
                <div class="btn-group">
                    ${arquivo.link_visualizacao ? `
                    <button class="btn btn-outline-success btn-sm" 
                            onclick="visualizarArquivoDrive('${arquivo.id}', '${arquivo.tipo}', '${escapeHtml(arquivo.nome)}')"
                            title="Visualizar no Drive">
                        <i class="fa-solid fa-eye"></i>
                    </button>
                    ` : ''}
                    
                    <a href="${arquivo.link_download}" 
                       class="btn btn-outline-primary btn-sm"
                       title="Download"
                       download="${escapeHtml(arquivo.nome)}">
                        <i class="fa-solid fa-download"></i>
                    </a>
                    
                    <a href="https://drive.google.com/file/d/${arquivo.id}/view" 
                       class="btn btn-outline-secondary btn-sm"
                       title="Abrir no Google Drive"
                       target="_blank">
                        <i class="fa-brands fa-google-drive"></i>
                    </a>
                </div>
            </div>
        </div>`;
    });
    
    html += '</div>';
    return html;
}

function renderizarMensagemVaziaDrive(mensagem) {
    return `
    <div class="alert alert-info">
        <i class="fa-solid fa-info-circle"></i>
        ${mensagem}
    </div>`;
}

function renderizarErroDrive(mensagem) {
    return `
    <div class="alert alert-danger">
        <i class="fa-solid fa-triangle-exclamation"></i>
        ${mensagem}
    </div>`;
}

function visualizarArquivoDrive(fileId, mimeType, fileName) {
    // Referências aos elementos do modal
    const modalElement = document.getElementById('driveModal');
    const modal = bootstrap.Modal.getOrCreateInstance(modalElement);
    const modalTitle = document.getElementById('driveModalTitle');
    const modalBody = document.getElementById('driveModalBody');
    const modalFooter = document.getElementById('driveModalFooter');

    // 1. Resetar e exibir o estado de loading
    modalTitle.textContent = fileName;
    modalFooter.innerHTML = ''; // Limpa o rodapé anterior
    
    // HTML do spinner de loading (Bootstrap)
    modalBody.innerHTML = `
        <div class="d-flex justify-content-center align-items-center" style="min-height: 250px;">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Carregando...</span>
            </div>
            <span class="ms-3">Carregando visualização...</span>
        </div>
    `;
    
    modal.show(); // Mostra o modal com o loading

    // URLs para nosso proxy
    const viewUrl = `/materiais/drive/download/${fileId}/?view=true`;
    const downloadUrl = `/materiais/drive/download/${fileId}/`;
    
    // 2. Criar e adicionar o botão de download no rodapé
    const downloadButtonHtml = `
        <a href="${downloadUrl}" class="btn btn-success" download="${escapeHtml(fileName)}">
            <i class="fa-solid fa-download me-2"></i>Baixar Arquivo
        </a>
        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Fechar</button>
    `;
    modalFooter.innerHTML = downloadButtonHtml;

    // 3. Carregar o conteúdo real do arquivo
    let contentHtml = '';

    // Para tipos de arquivos nativos do Google (Docs, Sheets, etc.)
    if (mimeType.includes('application/vnd.google-apps')) {
        contentHtml = `
            <div class="text-center py-4">
                <i class="fa-brands fa-google-drive fa-4x text-muted mb-3"></i>
                <h5>Este é um documento do Google</h5>
                <p class="text-muted">Ele precisa ser aberto diretamente no Google Drive.</p>
                <a href="https://drive.google.com/file/d/${fileId}/view" 
                   class="btn btn-primary" target="_blank">
                    <i class="fa-solid fa-arrow-up-right-from-square"></i> Abrir no Google Drive
                </a>
            </div>`;
        modalBody.innerHTML = contentHtml; // Substitui o spinner
    
    // Para imagens
    } else if (mimeType.startsWith('image/')) {
        const img = new Image();
        img.src = viewUrl;
        img.className = 'img-fluid';
        img.style = 'width: 100%; height: auto; border-radius: 8px;';
        img.alt = escapeHtml(fileName);
        img.onload = () => { // Espera a imagem carregar para substituir o spinner
            modalBody.innerHTML = '';
            modalBody.appendChild(img);
        };
        img.onerror = () => { // Caso ocorra um erro no carregamento
            modalBody.innerHTML = '<div class="alert alert-danger">Erro ao carregar a imagem.</div>';
        };
    
    // Para PDFs, Vídeos ou Áudios (usando iframe ou tags específicas)
    } else if (mimeType === 'application/pdf' || mimeType.startsWith('video/') || mimeType.startsWith('audio/')) {
        let mediaTag = '';
        if (mimeType === 'application/pdf') {
            mediaTag = `<iframe src="${viewUrl}" frameborder="0" allowfullscreen style="width: 100%; height: 100%; border-radius: 8px;"></iframe>`;
        } else if (mimeType.startsWith('video/')) {
            mediaTag = `<video controls src="${viewUrl}" style="width: 100%; height: 100%; border-radius: 8px;">Vídeo não suportado.</video>`;
        } else if (mimeType.startsWith('audio/')) {
            mediaTag = `<audio controls src="${viewUrl}" style="width: 100%;">Áudio não suportado.</audio>`;
        }
        
        contentHtml = `<div class="ratio ratio-16x9">${mediaTag}</div>`;
        // Para iframes e tags de mídia, a substituição pode ser direta,
        // pois o navegador gerencia o estado de loading interno.
        modalBody.innerHTML = contentHtml;

    // Para outros tipos de arquivo
    } else {
        contentHtml = `
            <div class="text-center py-4">
                <i class="fa-regular fa-file fa-4x text-muted mb-3"></i>
                <h5>Visualização não disponível</h5>
                <p class="text-muted">Este tipo de arquivo precisa ser baixado.</p>
            </div>`;
        modalBody.innerHTML = contentHtml; // Substitui o spinner
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Tooltips para os botões
document.addEventListener('DOMContentLoaded', function() {
    // Tooltips para materiais do sistema (já existentes)
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});