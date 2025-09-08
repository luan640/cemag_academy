document.addEventListener('DOMContentLoaded', function() {
    // Função para extrair o ID do arquivo do Google Drive
    function extractFileId(driveUrl) {
        const patterns = [
            /\/file\/d\/([^\/]+)/,
            /id=([^&]+)/,
            /[-\w]{25,}/
        ];
        
        for (const pattern of patterns) {
            const match = driveUrl.match(pattern);
            if (match && match[1]) {
                return match[1];
            } else if (match && match[0] && !match[0].includes('/')) {
                return match[0];
            }
        }
        return driveUrl;
    }

    // Event listener para os botões do Drive
    document.querySelectorAll('.drive-download-btn').forEach(button => {
        button.addEventListener('click', async function(e) {
            e.preventDefault();
            
            const driveUrl = this.getAttribute('data-file-id');
            const fileId = extractFileId(driveUrl);
            
            if (!fileId) {
                alert('Erro ao acessar o arquivo do Drive');
                return;
            }

            // Adiciona spinner de carregamento
            const originalHtml = this.innerHTML;
            this.innerHTML = '<span class="spinner-border spinner-border-sm" role="status"></span>';
            this.disabled = true;

            try {
                // Primeiro obtém a metadata para pegar o nome do arquivo
                const metadataResponse = await fetch(`/materiais/drive/metadata/${fileId}/`);
                
                if (!metadataResponse.ok) {
                    throw new Error('Erro ao obter informações do arquivo');
                }

                const metadataData = await metadataResponse.json();
                
                if (!metadataData.success) {
                    throw new Error(metadataData.error);
                }

                const metadata = metadataData.metadata;
                const mimeType = metadata.mimeType;
                const originalName = metadata.name;
                
                let endpoint;
                let exportMimeType = null;

                // Verifica se é um arquivo do Google Workspace que precisa de exportação
                exportMimeType = needsGoogleWorkspaceExport(mimeType);
                
                if (exportMimeType) {
                    // É um arquivo do Google Workspace - usa endpoint de exportação
                    endpoint = `/materiais/drive/export-google-file/${fileId}/?exportMimeType=${encodeURIComponent(exportMimeType)}&originalName=${encodeURIComponent(originalName)}`;
                } else {
                    // É um arquivo normal - usa endpoint de download SEM view=true
                    endpoint = `/materiais/drive/download/${fileId}/`;
                }

                const response = await fetch(endpoint);
                
                if (!response.ok) {
                    throw new Error(`Erro ${response.status}: ${response.statusText}`);
                }

                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                
                // SEMPRE faz download, nunca abre para visualização
                const a = document.createElement('a');
                a.style.display = 'none';
                a.href = url;
                
                let fileName = originalName;
                
                // Adiciona extensão correta para arquivos exportados
                if (exportMimeType) {
                    const extension = getFileExtension(exportMimeType);
                    if (extension && !fileName.endsWith(extension)) {
                        fileName += extension;
                    }
                } else {
                    // Para arquivos normais, tenta determinar a extensão
                    const extension = getExtensionFromMimeType(mimeType);
                    if (extension && !fileName.includes('.')) {
                        fileName += extension;
                    }
                }
                
                a.download = fileName;
                document.body.appendChild(a);
                a.click();
                
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);

            } catch (error) {
                console.error('Erro ao processar arquivo:', error);
                alert('Falha ao baixar o arquivo. Tente novamente.');
            } finally {
                // Restaura o botão original
                this.innerHTML = originalHtml;
                this.disabled = false;
            }
        });
    });
});


function getExtensionFromMimeType(mimeType) {
    const mimeToExtension = {
        'image/jpeg': '.jpg',
        'image/png': '.png',
        'image/gif': '.gif',
        'image/webp': '.webp',
        'image/svg+xml': '.svg',
        'application/pdf': '.pdf',
        'application/zip': '.zip',
        'text/plain': '.txt',
        'text/csv': '.csv',
        'application/msword': '.doc',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
        'application/vnd.ms-excel': '.xls',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': '.xlsx',
        'application/vnd.ms-powerpoint': '.ppt',
        'application/vnd.openxmlformats-officedocument.presentationml.presentation': '.pptx'
    };
    
    return mimeToExtension[mimeType] || '';
}

// Função para detectar tipos de arquivos do Google Workspace que precisam de exportação
function needsGoogleWorkspaceExport(mimeType) {
    const googleWorkspaceMimeTypes = {
        // Planilhas Google
        'application/vnd.google-apps.spreadsheet': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'application/vnd.google-apps.spreadsheets': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        
        // Documentos Google Docs
        'application/vnd.google-apps.document': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/vnd.google-apps.docs': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        
        // Apresentações Google Slides
        'application/vnd.google-apps.presentation': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        'application/vnd.google-apps.slides': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        
        // Desenhos Google Drawings
        'application/vnd.google-apps.drawing': 'image/png',
        
        // Formulários Google Forms (exporta como PDF)
        'application/vnd.google-apps.form': 'application/pdf',
        
        // Google Sites (exporta como ZIP)
        'application/vnd.google-apps.site': 'application/zip'
    };
    
    return googleWorkspaceMimeTypes[mimeType] || null;
}

// Função para obter a extensão do arquivo baseado no mimeType de exportação
function getFileExtension(exportMimeType) {
    const extensions = {
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': '.xlsx',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
        'application/vnd.openxmlformats-officedocument.presentationml.presentation': '.pptx',
        'image/png': '.png',
        'application/pdf': '.pdf',
        'application/zip': '.zip',
        'text/plain': '.txt',
        'text/csv': '.csv'
    };
    
    return extensions[exportMimeType] || '';
}