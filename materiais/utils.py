from googleapiclient.discovery import build
from google.oauth2 import service_account
from django.conf import settings
from django.core.cache import cache
from materiais.models import Pasta,Material,Visualizacao
import logging
import re

logger = logging.getLogger(__name__)

class ProgressoTrilha:

    def __init__(self, funcionario, pastas):
        self.funcionario = funcionario
        self.pastas = pastas

    def calcular_progresso_pasta(self, pasta):
        materiais_count = Material.objects.filter(pasta=pasta).count()
        visualizacoes_count = Visualizacao.objects.filter(
            funcionario=self.funcionario,
            material__pasta=pasta
        ).count()

        progresso = (visualizacoes_count / materiais_count) * 100 if materiais_count > 0 else 0
        return progresso

    def calcular_progresso_trilhas(self):
        progresso_pasta = {
            pasta.nome: self.calcular_progresso_pasta(pasta) for pasta in self.pastas
        }
        return progresso_pasta

    def calcular_media_progresso_area_trilha(self, progresso_pasta, pastas):
        progresso_por_area = {}
        contagem_por_area = {}

        for pasta in pastas:
            area_trilha = pasta.area_trilha.nome
            progresso = progresso_pasta.get(pasta.nome, 0)

            if area_trilha not in progresso_por_area:
                progresso_por_area[area_trilha] = 0
                contagem_por_area[area_trilha] = 0

            progresso_por_area[area_trilha] += progresso
            contagem_por_area[area_trilha] += 1

        media_progresso_area_trilha = {
            area_trilha: progresso / contagem_por_area[area_trilha]
            for area_trilha, progresso in progresso_por_area.items()
        }

        return media_progresso_area_trilha


class Drive:

    """Classe para gerenciar operações com Google Drive"""
    
    def __init__(self):
        self.scopes = settings.GOOGLE_DRIVE_SCOPES
        self.credentials_file = settings.GOOGLE_DRIVE_CREDENTIALS_FILE
        self.service = None
    
    def _build_service(self):
        """Constrói o serviço do Google Drive"""
        try:
            creds = service_account.Credentials.from_service_account_file(
                self.credentials_file, 
                scopes=self.scopes
            )
            self.service = build('drive', 'v3', credentials=creds)
            return self.service
        except Exception as e:
            logger.error(f"Erro ao construir serviço do Drive: {e}")
            raise
    
    def get_service(self):
        """Retorna o serviço do Drive, construindo se necessário"""
        if self.service is None:
            return self._build_service()
        return self.service
    
    def listar_arquivos_pasta(self, folder_id_or_url, cache_timeout=300):
        """Lista arquivos de uma pasta do Drive, aceitando URL ou ID"""
        # Extrai o ID real da URL ou valor fornecido
        folder_id = self.extrair_id_drive(folder_id_or_url)
        
        if not folder_id:
            logger.error(f"ID da pasta do Drive inválido: {folder_id_or_url}")
            return []
        
        cache_key = f"drive_files_{folder_id}"
        
        # Tenta obter do cache primeiro
        cached_files = cache.get(cache_key)
        if cached_files:
            return cached_files
        
        try:
            service = self.get_service()
            query = f"'{folder_id}' in parents and trashed = false"
            
            results = service.files().list(
                q=query,
                fields="files(id, name, mimeType, webViewLink, webContentLink, thumbnailLink, modifiedTime, size, fileExtension)",
                pageSize=100,
                supportsAllDrives=True,
                includeItemsFromAllDrives=True,
                orderBy="name"
            ).execute()
            
            files = results.get('files', [])
            
            # Armazena no cache
            cache.set(cache_key, files, cache_timeout)
            
            return files
            
        except Exception as e:
            logger.error(f"Erro ao listar arquivos da pasta {folder_id}: {e}")
            return []
    
    def obter_arquivo_por_id(self, file_id):
        """Obtém informações de um arquivo específico"""
        try:
            service = self.get_service()
            file = service.files().get(
                fileId=file_id,
                fields="id, name, mimeType, webViewLink, webContentLink, thumbnailLink, modifiedTime, size, fileExtension",
                supportsAllDrives=True
            ).execute()
            return file
        except Exception as e:
            logger.error(f"Erro ao obter arquivo {file_id}: {e}")
            return None
    
    @staticmethod
    def gerar_link_visualizacao(file_id, mime_type):
        """Gera link de visualização baseado no tipo de arquivo"""
        # Links para documentos do Google
        if mime_type == "application/vnd.google-apps.document":
            return f"https://docs.google.com/document/d/{file_id}/preview"
        elif mime_type == "application/vnd.google-apps.spreadsheet":
            return f"https://docs.google.com/spreadsheets/d/{file_id}/preview"
        elif mime_type == "application/vnd.google-apps.presentation":
            return f"https://docs.google.com/presentation/d/{file_id}/preview"
        elif mime_type == "application/vnd.google-apps.form":
            return f"https://docs.google.com/forms/d/{file_id}/preview"
        
        # Links para arquivos normais
        elif mime_type == "application/pdf":
            return f"https://drive.google.com/file/d/{file_id}/preview"
        elif mime_type.startswith("image/"):
            return f"https://drive.google.com/uc?id={file_id}"
        elif mime_type.startswith("video/"):
            return f"https://drive.google.com/uc?id={file_id}"
        elif mime_type.startswith("audio/"):
            return f"https://drive.google.com/uc?id={file_id}"
        else:
            return None
    
    @staticmethod
    def gerar_link_download(file_id):
        """Gera link de download direto"""
        return f"https://drive.google.com/uc?id={file_id}&export=download"
    
    @staticmethod
    def formatar_tamanho_arquivo(bytes_size):
        """Formata o tamanho do arquivo para leitura humana"""
        if not bytes_size:
            return "N/A"
        
        try:
            bytes_size = int(bytes_size)
        except (ValueError, TypeError):
            return "N/A"
        
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.1f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.1f} TB"
    
    @staticmethod
    def obter_icone_por_tipo(mime_type):
        """Retorna classe do ícone baseado no tipo de arquivo"""
        icon_map = {
            # Google Docs
            "application/vnd.google-apps.document": "fa-file-word text-primary",
            "application/vnd.google-apps.spreadsheet": "fa-file-excel text-success",
            "application/vnd.google-apps.presentation": "fa-file-powerpoint text-danger",
            "application/vnd.google-apps.form": "fa-file-lines text-info",
            
            # Documentos
            "application/pdf": "fa-file-pdf text-danger",
            "application/msword": "fa-file-word text-primary",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "fa-file-word text-primary",
            "application/vnd.ms-excel": "fa-file-excel text-success",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "fa-file-excel text-success",
            "application/vnd.ms-powerpoint": "fa-file-powerpoint text-danger",
            "application/vnd.openxmlformats-officedocument.presentationml.presentation": "fa-file-powerpoint text-danger",
            
            # Imagens
            "image/jpeg": "fa-file-image text-info",
            "image/png": "fa-file-image text-info",
            "image/gif": "fa-file-image text-info",
            "image/svg+xml": "fa-file-image text-info",
            
            # Vídeos
            "video/mp4": "fa-file-video text-warning",
            "video/avi": "fa-file-video text-warning",
            "video/mkv": "fa-file-video text-warning",
            "video/quicktime": "fa-file-video text-warning",
            
            # Áudios
            "audio/mpeg": "fa-file-audio text-secondary",
            "audio/wav": "fa-file-audio text-secondary",
            
            # Arquivos
            "text/plain": "fa-file-lines text-secondary",
            "text/csv": "fa-file text-success",
            "application/zip": "fa-file-zipper text-warning",
            "application/x-rar-compressed": "fa-file-zipper text-warning",
        }
        
        return icon_map.get(mime_type, "fa-file text-secondary")
    
    def limpar_cache_pasta(self, folder_id):
        """Remove arquivos do cache para uma pasta específica"""
        cache_key = f"drive_files_{folder_id}"
        cache.delete(cache_key)
        logger.info(f"Cache limpo para pasta: {folder_id}")
    
    @staticmethod
    def extrair_id_drive(url_ou_id):
        """
        Extrai o ID do Google Drive de uma URL ou retorna o próprio valor se já for um ID
        
        Exemplos:
        - '1c0MiC81UZ5nl3Ckr_uERYxx0MMA-ZGmH' → '1c0MiC81UZ5nl3Ckr_uERYxx0MMA-ZGmH'
        - 'https://drive.google.com/drive/folders/1c0MiC81UZ5nl3Ckr_uERYxx0MMA-ZGmH?usp=drive_link' → '1c0MiC81UZ5nl3Ckr_uERYxx0MMA-ZGmH'
        - 'https://drive.google.com/open?id=1c0MiC81UZ5nl3Ckr_uERYxx0MMA-ZGmH' → '1c0MiC81UZ5nl3Ckr_uERYxx0MMA-ZGmH'
        """
        if not url_ou_id:
            return None
        
        # Se parece ser apenas um ID (sem caracteres de URL)
        if len(url_ou_id) in [33, 44] and '/' not in url_ou_id and ':' not in url_ou_id:
            return url_ou_id
        
        # Padrões de regex para URLs do Google Drive
        patterns = [
            r'[/=]([0-9A-Za-z_-]{33})[/?]?',  # IDs de 33 caracteres
            r'[/=]([0-9A-Za-z_-]{44})[/?]?',  # IDs de 44 caracteres (mais raros)
            r'folders/([0-9A-Za-z_-]+)',      # Pattern específico para folders
            r'id=([0-9A-Za-z_-]+)'           # Pattern para parâmetro id=
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url_ou_id)
            if match:
                return match.group(1)
        
        # Se não encontrou padrão, retorna o valor original (pode ser um ID válido)
        return url_ou_id if len(url_ou_id) in [33, 44] else None