from googleapiclient.discovery import build
from google.oauth2 import service_account
from django.conf import settings
from django.core.cache import cache
from materiais.models import Pasta,Material,Visualizacao
import logging
import re
import json
import os

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
        self.service = None

    def _build_service(self):
        """Constrói o serviço do Google Drive a partir de variáveis de ambiente separadas"""
        try:
            # CORREÇÃO: Usamos .strip('\'",') para remover aspas e vírgulas extras
            def clean_env_var(var_name):
                return os.getenv(var_name, '').strip('\'",')

            private_key = clean_env_var('GOOGLE_PRIVATE_KEY').replace('\\n', '\n')

            if not private_key:
                raise ValueError("A variável de ambiente 'GOOGLE_PRIVATE_KEY' não foi definida ou está vazia.")

            credentials_info = {
                "type": clean_env_var('GOOGLE_TYPE'),
                "project_id": clean_env_var('GOOGLE_PROJECT_ID'),
                "private_key_id": clean_env_var('GOOGLE_PRIVATE_KEY_ID'),
                "private_key": private_key,
                "client_email": clean_env_var('GOOGLE_CLIENT_EMAIL'),
                "client_id": clean_env_var('GOOGLE_CLIENT_ID'),
                "auth_uri": clean_env_var('GOOGLE_AUTH_URI'),
                "token_uri": clean_env_var('GOOGLE_TOKEN_URI'),
                "auth_provider_x509_cert_url": clean_env_var('GOOGLE_AUTH_PROVIDER_X509_CERT_URL'),
                "client_x509_cert_url": clean_env_var('GOOGLE_CLIENT_X509_CERT_URL'),
            }

            if not all(value for key, value in credentials_info.items() if key != 'private_key' and not value):
                 raise ValueError("Uma ou mais variáveis de ambiente do Google Drive não foram definidas.")

            creds = service_account.Credentials.from_service_account_info(
                credentials_info,
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
        folder_id = self.extrair_id_drive(folder_id_or_url)
        if not folder_id:
            logger.error(f"ID da pasta do Drive inválido: {folder_id_or_url}")
            return []

        cache_key = f"drive_files_{folder_id}"
        cached_files = cache.get(cache_key)
        if cached_files is not None:
            return cached_files

        try:
            service = self.get_service()
            if not service:
                raise Exception("Serviço do Google Drive não pôde ser inicializado.")

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
            cache.set(cache_key, files, cache_timeout)
            return files
        except Exception as e:
            logger.error(f"Erro ao listar arquivos da pasta {folder_id}: {e}")
            return []

    def obter_arquivo_por_id(self, file_id):
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
        if not url_ou_id:
            return None
        patterns = [
            r'folders/([0-9A-Za-z_-]{20,})',
            r'id=([0-9A-Za-z_-]{20,})',
            r'/d/([0-9A-Za-z_-]{20,})'
        ]
        for pattern in patterns:
            match = re.search(pattern, url_ou_id)
            if match:
                return match.group(1)
        if len(url_ou_id) > 20 and '/' not in url_ou_id and ':' not in url_ou_id:
            return url_ou_id
        return None