document.addEventListener('DOMContentLoaded', function() {
    const listaMateriais = document.getElementById('lista-materiais');
    
    if (!listaMateriais) {
        return;
    }
    
    const hasDrive = listaMateriais.getAttribute('data-has-drive') === 'true';
    const pastaId = listaMateriais.getAttribute('data-pasta-id');
    
    if (hasDrive && pastaId) {
        carregarArquivosDrive(pastaId);
    }
});

// Tooltips para os bot?es (opcional, s? se bootstrap estiver carregado)
document.addEventListener('DOMContentLoaded', function() {
    if (window.bootstrap && bootstrap.Tooltip) {
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
});



function carregarArquivosDrive(pastaId) {
    const loadingElement = document.getElementById('drive-loading');
    const driveContent = document.getElementById('drive-content');
    
    // Na tela de detalhes, usamos o endpoint filtrado
    fetch(`/materiais/pasta/${pastaId}/drive-filtrado/`)
        .then(response => response.json())
        .then(data => {
            if (data.success && data.arquivos.length > 0) {
                console.log(data);

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
    const modal = ensureDriveModal();

    const showLoading = () => {
        modal.show();
        modal.setContent({
            title: fileName || 'Arquivo do Drive',
            body: '<div class="drive-modal-loading">Carregando...</div>',
            footer: ''
        });
    };

    // Se o tipo n??o foi informado, busca a metadata primeiro
    if (!mimeType) {
        showLoading();
        fetch(`/materiais/drive/metadata/${fileId}/`)
            .then(response => response.json())
            .then(data => {
                if (data.success && data.metadata) {
                    const meta = data.metadata;
                    visualizarArquivoDrive(fileId, meta.mimeType, meta.name || fileName);
                } else {
                    modal.setContent({
                        title: fileName || 'Arquivo do Drive',
                        body: '<div class="alert alert-danger">Erro ao obter informa??es do arquivo do Drive.</div>',
                    });
                }
            })
            .catch(() => {
                modal.setContent({
                    title: fileName || 'Arquivo do Drive',
                    body: '<div class="alert alert-danger">Erro ao obter informa??es do arquivo do Drive.</div>',
                });
            });
        return;
    }

    showLoading();

    const exportUrl = `/materiais/drive/export/${fileId}/`;

    if (mimeType === 'application/vnd.google-apps.spreadsheet') {
        modal.setContent({
            title: fileName,
            body: `
            <div class="text-center py-4">
                <i class="fa-solid fa-file-excel fa-4x text-success mb-3"></i>
                <h5>Exportar como Planilha Excel</h5>
                <p class="text-muted">Este arquivo é uma Planilha Google. A visualização direta não é possível, mas você pode exportá-la para o formato Excel (.xlsx).</p>
            </div>`,
            footer: `
            <a href="${exportUrl}" 
            class="btn btn-success btn-download-drive" 
            download="${escapeHtml(fileName)}"
            data-file-id="${fileId}"
            data-mime-type="${mimeType}"
        `
        });
    } else if (mimeType.includes('application/vnd.google-apps')) {
        const downloadUrl = `/materiais/drive/download/${fileId}/`;
        modal.setContent({
            title: fileName,
            body: `
            <div class="text-center py-4">
                <i class="fa-brands fa-google-drive fa-4x text-muted mb-3"></i>
                <h5>Visualização não disponível</h5>
                <p class="text-muted">Este tipo de arquivo do Google precisa ser baixado.</p>
            </div>`,
            footer: `
            <a href="${downloadUrl}" 
            class="btn btn-primary btn-download-drive" 
            download="${escapeHtml(fileName)}"
            data-file-id="${fileId}"
            data-mime-type="${mimeType}"
        `
        });
    } else {
        const viewUrl = `/materiais/drive/download/${fileId}/?view=true`;
        const downloadUrl = `/materiais/drive/download/${fileId}/`;

        modal.setContent({
            title: fileName,
            body: '<div class="drive-modal-loading">Carregando...</div>',
            footer: `
            <a href="${downloadUrl}" 
            class="btn btn-success btn-download-drive" 
            download="${escapeHtml(fileName)}"
            data-file-id="${fileId}"
            data-mime-type="${mimeType}"
        `
        });

        if (mimeType.startsWith('image/')) {
            const img = new Image();
            img.src = viewUrl;
            img.className = 'img-fluid';
            img.onload = () => modal.setBody(`<div style="text-align:center"><img src="${viewUrl}" alt="${escapeHtml(fileName)}" style="max-width:100%; max-height:70vh; border-radius:6px;" /></div>`);
            img.onerror = () => modal.setBody('<div class="alert alert-danger">Erro ao carregar a imagem.</div>');
        } else if (mimeType === 'application/pdf' || mimeType.startsWith('video/')) {
            const mediaTag = (mimeType === 'application/pdf')
                ? `<iframe src="${viewUrl}" frameborder="0"></iframe>`
                : `<video controls src="${viewUrl}">Vídeo não suportado.</video>`;
            modal.setBody(`
                <div class="drive-media">
                    <div class="drive-media-loading"><div class="drive-spinner"></div><span>Carregando...</span></div>
                    ${mediaTag}
                </div>`);

            const mediaElement = document.querySelector('#drive-modal-body iframe, #drive-modal-body video');
            const loader = document.querySelector('#drive-modal-body .drive-media-loading');
            const removeLoader = () => { if (loader) loader.remove(); if (mediaElement) mediaElement.style.opacity = '1'; };
            if (mediaElement) {
                mediaElement.addEventListener(mimeType === 'application/pdf' ? 'load' : 'loadeddata', removeLoader, { once: true });
                mediaElement.addEventListener('error', () => {
                    modal.setBody(`
                        <div class="alert alert-danger">
                            Não foi possível carregar o arquivo no modal.
                            <div class="mt-2">
                                <a class="btn btn-primary btn-sm" href="${downloadUrl}" target="_blank" rel="noopener">Abrir / baixar</a>
                            </div>
                        </div>`);
                });
            }
        } else {
            modal.setBody(`
                <div class="text-center py-4">
                    <i class="fa-regular fa-file fa-4x text-muted mb-3"></i>
                    <h5>Visualiza??o n?o dispon?vel</h5>
                    <p class="text-muted">Este tipo de arquivo precisa ser baixado.</p>
                </div>`);
        }
    }
}

function ensureDriveModal() {
    let root = document.getElementById('drive-modal-root');
    if (!root) {
        root = document.createElement('div');
        root.id = 'drive-modal-root';
        root.innerHTML = `
        <style>
            #drive-modal-root {
                position: fixed;
                inset: 0;
                display: none;
                align-items: center;
                justify-content: center;
                background: rgba(0,0,0,0.55);
                z-index: 1050;
                padding: 20px;
            }
            .drive-modal {
                background: #fff;
                border-radius: 10px;
                max-width: 1100px;
                width: 95%;
                max-height: 92vh;
                display: flex;
                flex-direction: column;
                box-shadow: 0 12px 30px rgba(0,0,0,0.25);
                overflow: hidden;
            }
            .drive-modal-header, .drive-modal-footer {
                padding: 16px;
                border-bottom: 1px solid #e9ecef;
                background: #f9fbfe;
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 10px;
            }
            .drive-modal-footer { border-top: 1px solid #e9ecef; border-bottom: none; }
            .drive-modal-body {
                padding: 16px;
                overflow: auto;
                max-height: 75vh;
                background: #f7f9fc;
            }
            .drive-modal-close {
                background: none;
                border: 1px solid transparent;
                color: #0f4c75;
                font-size: 1.2rem;
                line-height: 1;
                cursor: pointer;
                width: 32px;
                height: 32px;
                border-radius: 50%;
                display: inline-flex;
                align-items: center;
                justify-content: center;
                transition: background 0.2s ease, color 0.2s ease, border-color 0.2s ease;
            }
            .drive-modal-close:hover {
                background: #e8f1fb;
                border-color: #d5e4f5;
                color: #0a3b5c;
            }
            .drive-modal-loading {
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 40px 0;
                gap: 10px;
            }
            .drive-media {
                position: relative;
                width: 100%;
                height: 65vh;
                background: #0e1724;
                border-radius: 8px;
                overflow: hidden;
            }
            .drive-media iframe,
            .drive-media video {
                width: 100%;
                height: 100%;
                border: 0;
                opacity: 0;
                transition: opacity 0.25s ease;
                background: #0e1724;
            }
            .drive-media-loading {
                position: absolute;
                inset: 0;
                display: flex;
                align-items: center;
                justify-content: center;
                background: rgba(0,0,0,0.35);
                color: #fff;
                font-weight: 600;
                z-index: 2;
                gap: 10px;
            }
            .drive-spinner {
                width: 36px;
                height: 36px;
                border: 4px solid rgba(255,255,255,0.35);
                border-top-color: #0f4c75;
                border-radius: 50%;
                animation: drive-spin 0.9s linear infinite;
            }
            @keyframes drive-spin { to { transform: rotate(360deg); } }
        </style>
        <div class="drive-modal" role="dialog" aria-modal="true">
            <div class="drive-modal-header">
                <h5 class="mb-0 drive-modal-title">Arquivo</h5>
                <button class="drive-modal-close" data-drive-modal-close aria-label="Fechar">&times;</button>
            </div>
            <div class="drive-modal-body" id="drive-modal-body"></div>
            <div class="drive-modal-footer d-flex gap-2 flex-wrap justify-content-end" id="drive-modal-footer"></div>
        </div>`;
        document.body.appendChild(root);

    }

    const titleEl = root.querySelector('.drive-modal-title');
    const bodyEl = root.querySelector('#drive-modal-body');
    const footerEl = root.querySelector('#drive-modal-footer');
    const closeEls = root.querySelectorAll('[data-drive-modal-close]');

    function hide() {
        root.style.display = 'none';
        bodyEl.innerHTML = '';
        footerEl.innerHTML = '';
    }

    function show() {
        root.style.display = 'flex';
    }

    function setContent({ title = '', body = '', footer = '' }) {
        if (titleEl) titleEl.textContent = title;
        if (bodyEl) bodyEl.innerHTML = body;
        if (footerEl) {
            footerEl.innerHTML = footer;
            footerEl.querySelectorAll('[data-drive-modal-close]').forEach(btn => btn.addEventListener('click', hide));
        }
        closeEls.forEach(btn => btn.addEventListener('click', hide));
    }

    function setBody(html) {
        if (bodyEl) bodyEl.innerHTML = html;
    }

    return { show, hide, setContent, setBody };
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

// Disponibiliza funções usadas em atributos onclick no escopo global
window.visualizarArquivoDrive = visualizarArquivoDrive;
window.handleDownloadClick = handleDownloadClick;
window.limparCachePasta = limparCachePasta;
