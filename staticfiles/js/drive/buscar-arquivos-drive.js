import { renderizarMensagemVaziaDrive, renderizarErroDrive, escapeHtml } from './carregar_arquivos_drive.js';

// Essa função será chamada toda vez que o usuário digitar no input
function handlePastaDriveInput(event) {
    const valor = event.target.value;
    const pastaId = document.getElementById('pasta_id').value;

    carregarArquivosDrive(pastaId)

}

function carregarArquivosDrive(pastaId) {
    const driveContent = document.getElementById('drive-content');
    
    fetch(`/materiais/pasta/${pastaId}/drive/`)
        .then(response => response.json())
        .then(data => {
            if (data.success && data.arquivos.length > 0) {
                console.log(data);

                driveContent.innerHTML = renderizarArquivosDrive(
                    data.arquivos, 
                    data.pasta_id
                );
                
                const driveSectionElement = document.getElementById("drive-section");
                driveSectionElement.style.display = 'block';

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
            <div class="form-check mb-0">
                <input 
                    class="form-check-input" 
                    type="checkbox" 
                    id="drive-select-all"
                >
                <label class="form-check-label" for="drive-select-all">
                    Selecionar todos os arquivos
                </label>
            </div>
        </div>`;

    
    arquivos.forEach(arquivo => {
        const deveEstarMarcado =
            (typeof arquivo.selecionado !== 'undefined' && arquivo.selecionado) ||
            (Array.isArray(window.ARQUIVOS_DRIVE_SELECIONADOS) &&
             window.ARQUIVOS_DRIVE_SELECIONADOS.includes(arquivo.id));

        html += `
        <div class="list-group-item list-group-item-action flex-column align-items-start drive-item">
            <div class="d-flex w-100 justify-content-between align-items-center">
                
                <div class="d-flex align-items-center" style="gap: 15px;">
                    <!-- Checkbox ao lado do arquivo -->
                    <div class="form-check mb-0">
                        <input 
                            class="form-check-input drive-file-checkbox" 
                            type="checkbox" 
                            value="${arquivo.id}" 
                            id="drive-file-${arquivo.id}"
                            data-file-id="${arquivo.id}"
                            data-file-name="${escapeHtml(arquivo.nome)}"
                            ${deveEstarMarcado ? 'checked' : ''}
                        >
                    </div>

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

document.addEventListener('change', function (event) {
    const target = event.target;

    // Quando mudar o checkbox "selecionar todos"
    if (target && target.id === 'drive-select-all') {
        const marcar = target.checked;

        // Marca/desmarca todos os checkboxes dos arquivos
        document.querySelectorAll('.drive-file-checkbox').forEach(cb => {
            cb.checked = marcar;
        });

        // Atualiza campos ocultos com os arquivos selecionados
        atualizarInputsArquivosDriveSelecionados();
    }
});

// Atualiza os inputs ocultos com os IDs dos arquivos selecionados
function atualizarInputsArquivosDriveSelecionados() {
    const container = document.getElementById('drive-selected-inputs');
    if (!container) {
        return;
    }

    container.innerHTML = '';

    const selecionados = document.querySelectorAll('.drive-file-checkbox:checked');
    selecionados.forEach((checkbox) => {
        const hiddenInput = document.createElement('input');
        hiddenInput.type = 'hidden';
        hiddenInput.name = 'arquivos_drive_ids';
        hiddenInput.value = checkbox.dataset.fileId;
        container.appendChild(hiddenInput);
    });
}

// Quando o DOM carregar, conecta o evento ao input
document.addEventListener("DOMContentLoaded", function () {
    // Se o Django estiver usando o id padrão, será algo como id_pasta_drive.
    // Ajuste o seletor se for diferente.
    const pastaId = document.getElementById('pasta_id').value;

    const inputPastaDriveElement = document.getElementById('id_pasta_drive').value;

    if (inputPastaDriveElement){
        carregarArquivosDrive(pastaId);
    }

    const inputPastaDrive =
        document.getElementById("id_pasta_drive") || 
        document.querySelector('input[name="pasta_drive"]');

    if (inputPastaDrive) {
        inputPastaDrive.addEventListener("input", handlePastaDriveInput);
    } else {
        console.warn("Input pasta_drive não encontrado na página.");
    }
});
