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
                driveContent.innerHTML = renderizarArquivosDrive(
                    data.arquivos, 
                    data.pasta_id
                );
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

function renderizarArquivosDrive(arquivos, pastaId) {
    let html = '<div class="list-group">';
    
    // Botão para limpar cache da pasta (no topo da lista)
    html += `
    <div class="list-group-item bg-light">
        <div class="d-flex justify-content-between align-items-center">
            <small class="text-muted">Atualizar pasta do drive</small>
            <button class="btn btn-outline-secondary btn-sm" 
                    onclick="limparCachePasta(${pastaId})"
                    title="Atualizar Pasta">
                <i class="fa-solid fa-broom me-1"></i>
                Atualizar dados do drive
            </button>
        </div>
    </div>`;
    
    
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
                            title="Visualizar">
                        <i class="fa-solid fa-eye"></i>
                    </button>
                    ` : ''}
                    
                    <a href="${arquivo.link_download}" 
                       class="btn btn-outline-primary btn-sm btn-download-drive"
                       title="Download"
                       download="${escapeHtml(arquivo.nome)}"
                       data-file-id="${arquivo.id}"
                       data-mime-type="${arquivo.tipo}"
                       onclick="handleDownloadClick(this, event)">
                        <span class="download-text">
                            <i class="fa-solid fa-download"></i>
                        </span>
                        <span class="download-loading d-none">
                            <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                            Carregando...
                        </span>
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
    const modalElement = document.getElementById('driveModal');
    const modal = bootstrap.Modal.getOrCreateInstance(modalElement);
    const modalTitle = document.getElementById('driveModalTitle');
    const modalBody = document.getElementById('driveModalBody');
    const modalFooter = document.getElementById('driveModalFooter');

    modalTitle.textContent = fileName;
    
    // URL para o novo endpoint de exportação que criaremos no backend
    const exportUrl = `/materiais/drive/export/${fileId}/`;
    
    // Limpa rodapé e mostra o loading
    modalFooter.innerHTML = '';
    modalBody.innerHTML = `
        <div class="d-flex justify-content-center align-items-center" style="min-height: 250px;">
            <div class="spinner-border text-primary" role="status"><span class="visually-hidden">Carregando...</span></div>
        </div>`;
    
    modal.show();

    // ** LÓGICA PRINCIPAL MODIFICADA **

    // CASO 1: É UMA PLANILHA GOOGLE
    if (mimeType === 'application/vnd.google-apps.spreadsheet') {
        modalBody.innerHTML = `
            <div class="text-center py-4">
                <i class="fa-solid fa-file-excel fa-4x text-success mb-3"></i>
                <h5>Exportar como Planilha Excel</h5>
                <p class="text-muted">Este arquivo é uma Planilha Google. A visualização direta não é possível, mas você pode exportá-la para o formato Excel (.xlsx).</p>
            </div>`;
        
        // Adiciona o botão de exportar no rodapé
        modalFooter.innerHTML = `
            <a href="${exportUrl}" 
            class="btn btn-success btn-download-drive" 
            download="${escapeHtml(fileName)}"
            data-file-id="${fileId}"
            data-mime-type="${mimeType}"
            onclick="handleDownloadClick(this, event)">
                <span class="download-text">
                    <i class="fa-solid fa-file-export me-2"></i>Exportar para XLSX
                </span>
                <span class="download-loading d-none">
                    <span class="spinner-border spinner-border-sm me-2" role="status"></span>
                    Exportando...
                </span>
            </a>
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Fechar</button>
        `;

    // CASO 2: É OUTRO TIPO DE ARQUIVO GOOGLE (DOC, SLIDE, ETC.)
    } else if (mimeType.includes('application/vnd.google-apps')) {
        modalBody.innerHTML = `
            <div class="text-center py-4">
                <i class="fa-brands fa-google-drive fa-4x text-muted mb-3"></i>
                <h5>Visualização não disponível</h5>
                <p class="text-muted">Este tipo de arquivo do Google precisa ser baixado.</p>
            </div>`;
        
        // Adiciona apenas o botão de download genérico
        const downloadUrl = `/materiais/drive/download/${fileId}/`;
        modalFooter.innerHTML = `
            <a href="${downloadUrl}" 
            class="btn btn-primary btn-download-drive" 
            download="${escapeHtml(fileName)}"
            data-file-id="${fileId}"
            data-mime-type="${mimeType}"
            onclick="handleDownloadClick(this, event)">
                <span class="download-text">
                    <i class="fa-solid fa-download me-2"></i>Baixar Arquivo
                </span>
                <span class="download-loading d-none">
                    <span class="spinner-border spinner-border-sm me-2" role="status"></span>
                    Baixando...
                </span>
            </a>
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Fechar</button>
        `;

    // CASO 3: ARQUIVOS VISUALIZÁVEIS (PDF, VÍDEO, IMAGEM, ETC.)
    } else {
        const viewUrl = `/materiais/drive/download/${fileId}/?view=true`;
        const downloadUrl = `/materiais/drive/download/${fileId}/`;
        
        // Adiciona o botão de download no rodapé
        modalFooter.innerHTML = `
            <a href="${downloadUrl}" 
            class="btn btn-success btn-download-drive" 
            download="${escapeHtml(fileName)}"
            data-file-id="${fileId}"
            data-mime-type="${mimeType}"
            onclick="handleDownloadClick(this, event)">
                <span class="download-text">
                    <i class="fa-solid fa-download me-2"></i>Baixar Arquivo
                </span>
                <span class="download-loading d-none">
                    <span class="spinner-border spinner-border-sm me-2" role="status"></span>
                    Baixando...
                </span>
            </a>
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Fechar</button>
        `;

        if (mimeType.startsWith('image/')) {
            const img = new Image();
            img.src = viewUrl;
            img.className = 'img-fluid';
            img.onload = () => { modalBody.innerHTML = ''; modalBody.appendChild(img); };
            img.onerror = () => { modalBody.innerHTML = '<div class="alert alert-danger">Erro ao carregar a imagem.</div>'; };
        } else if (mimeType === 'application/pdf' || mimeType.startsWith('video/')) {
            const mediaTag = (mimeType === 'application/pdf')
                ? `<iframe src="${viewUrl}" frameborder="0" style="width: 100%; height: 100%;"></iframe>`
                : `<video controls src="${viewUrl}" style="width: 100%; height: 100%;">Vídeo não suportado.</video>`;
            modalBody.innerHTML = `<div class="ratio ratio-16x9">${mediaTag}</div>`;
        } else {
            modalBody.innerHTML = `
                <div class="text-center py-4">
                    <i class="fa-regular fa-file fa-4x text-muted mb-3"></i>
                    <h5>Visualização não disponível</h5>
                    <p class="text-muted">Este tipo de arquivo precisa ser baixado.</p>
                </div>`;
        }
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function handleDownloadClick(button, event) {
    // Previne o comportamento padrão do link
    event.preventDefault();
    
    // Se já estiver desabilitado, não faz nada
    if (button.classList.contains('disabled')) {
        return false;
    }
    
    // Adiciona classes de loading e disabled
    button.classList.add('disabled');
    const downloadText = button.querySelector('.download-text');
    const downloadLoading = button.querySelector('.download-loading');
    
    downloadText.classList.add('d-none');
    downloadLoading.classList.remove('d-none');
    
    // Obtém os dados do arquivo
    const fileId = button.getAttribute('data-file-id');
    const mimeType = button.getAttribute('data-mime-type');
    const fileName = button.getAttribute('download');
    
    // Define a URL correta baseada no mimeType
    let downloadUrl;
    if (mimeType === 'application/vnd.google-apps.spreadsheet') {
        // Usa a URL de exportação para planilhas Google
        downloadUrl = `/materiais/drive/export/${fileId}/`;
    } else {
        // Usa a URL normal de download para outros arquivos
        downloadUrl = button.getAttribute('href');
    }
    
    // Faz a requisição para download
    fetch(downloadUrl)
        .then(response => {
            if (response.ok) {
                return response.blob();
            }
            throw new Error('Erro no download');
        })
        .then(blob => {
            // Cria um link temporário para download
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            
            // Define o nome do arquivo para download
            // Para planilhas Google, adiciona a extensão .xlsx
            let downloadFileName = fileName;
            if (mimeType === 'application/vnd.google-apps.spreadsheet' && !fileName.endsWith('.xlsx')) {
                downloadFileName = fileName + '.xlsx';
            }
            
            a.download = downloadFileName;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            // Restaura o botão após o download
            resetDownloadButton(button);
        })
        .catch(error => {
            console.error('Erro no download:', error);
            // Restaura o botão em caso de erro
            resetDownloadButton(button);
            alert('Erro ao baixar o arquivo. Tente novamente.');
        });
    
    return false;
}

function resetDownloadButton(button) {
    button.classList.remove('disabled');
    const downloadText = button.querySelector('.download-text');
    const downloadLoading = button.querySelector('.download-loading');
    
    downloadText.classList.remove('d-none');
    downloadLoading.classList.add('d-none');
}

function limparCachePasta(pastaId) {
    if (!confirm('Tem certeza que deseja limpar o cache de TODA a pasta?\nIsso forçará o recarregamento de todos os arquivos na próxima visualização.')) {
        return;
    }
    
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    // Mostra loading no botão
    const button = document.querySelector(`[onclick="limparCachePasta(${pastaId})"]`);
    const originalHtml = button.innerHTML;
    button.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Atualizando...';
    button.disabled = true;
    
    fetch(`/materiais/drive/clear/${pastaId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        // Restaura o botão
        button.innerHTML = originalHtml;
        button.disabled = false;
        
        if (data.success) {
            window.location.reload();
        } else {
            alert(data.error);
        }
    })
    .catch(error => {
        console.error('Erro:', error);
        // Restaura o botão em caso de erro
        button.innerHTML = originalHtml;
        button.disabled = false;
    });
}

// Tooltips para os botões
document.addEventListener('DOMContentLoaded', function() {
    // Tooltips para materiais do sistema (já existentes)
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});