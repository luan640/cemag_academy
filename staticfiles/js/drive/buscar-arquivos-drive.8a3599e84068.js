// Essa função será chamada toda vez que o usuário digitar no input
function handlePastaDriveInput(event) {
    const valor = event.target.value;
    const pastaId = document.getElementById('pasta_id').value;

    carregarArquivosDrive(pastaId)

}

export function renderizarMensagemVaziaDrive(mensagem) {
    return `
    <div class="alert alert-info">
        <i class="fa-solid fa-info-circle"></i>
        ${mensagem}
    </div>`;
}

export function renderizarErroDrive(mensagem) {
    return `
    <div class="alert alert-danger">
        <i class="fa-solid fa-triangle-exclamation"></i>
        ${mensagem}
    </div>`;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
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

function carregarArquivosDriveEdit() {
    const driveContent = document.getElementById('drive-content');
    const driveSectionElement = document.getElementById('drive-section');
    const inputPastaDrive = document.getElementById('id_pasta_drive');

    if (!inputPastaDrive) {
        console.warn('Campo id_pasta_drive não encontrado.');
        return;
    }

    const urlPastaDrive = inputPastaDrive.value.trim();

    // Se o campo estiver vazio, você pode esconder a seção ou só limpar
    if (!urlPastaDrive) {
        if (driveSectionElement) {
            driveSectionElement.style.display = 'none';
        }
        driveContent.innerHTML = '';
        console.log("vazio")
        return;
    }

    const params = new URLSearchParams({
        url_pasta_drive: urlPastaDrive,
    });

    fetch(`/materiais/buscar-arquivos-drive-url/?${params.toString()}`)
        .then(response => response.json())
        .then(data => {
            if (data.success && data.arquivos && data.arquivos.length > 0) {
                console.log(data);

                // sua API buscar_arquivos_drive_url NÃO retorna pasta_id,
                // então aqui passamos só os arquivos
                driveContent.innerHTML = renderizarArquivosDrive(
                    data.arquivos
                );

                if (driveSectionElement) {
                    driveSectionElement.style.display = 'block';
                }
            } else {
                driveContent.innerHTML = renderizarMensagemVaziaDrive(
                    data.error || 'Nenhum arquivo encontrado no Drive'
                );
                if (driveSectionElement) {
                    driveSectionElement.style.display = 'block';
                }
            }
        })
        .catch(error => {
            driveContent.innerHTML = renderizarErroDrive('Erro ao carregar arquivos do Drive');
            console.error('Erro:', error);
            if (driveSectionElement) {
                driveSectionElement.style.display = 'block';
            }
        });
}

function renderizarArquivosDrive(arquivos) {
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
                    </div>
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
    const pastaIdInput = document.getElementById('pasta_id');
    const inputPastaDrive =
        document.getElementById("id_pasta_drive") || 
        document.querySelector('input[name="pasta_drive"]');

    if (!pastaIdInput || !inputPastaDrive) {
        console.warn("pasta_id ou pasta_drive não encontrados na página.");
        return;
    }

    const pastaId = pastaIdInput.value;

    // Se já vier preenchido ao carregar a página
    if (inputPastaDrive.value.trim() !== "") {
        carregarArquivosDrive(pastaId);
    }

    // Também chamar quando o usuário DIGITAR algo
    inputPastaDrive.addEventListener("input", function (event) {
        const valor = event.target.value.trim();
        console.log(valor);

        // Só chama se tiver algo digitado (não vazio)
        if (valor !== "") {
            carregarArquivosDriveEdit(pastaId);
        }
    });
});
