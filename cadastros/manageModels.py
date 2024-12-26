from django.db import models

class FuncionarioManager(models.Manager):
    def get_queryset(self):
        # Filtro global para incluir apenas os registros não excluídos
        return super().get_queryset().filter(excluido=False)
    
class AreaManager(models.Manager):
    def get_queryset(self):
        # Filtro global para incluir apenas os registros não excluídos
        return super().get_queryset().filter(excluido=False)
    
class SetorManager(models.Manager):
    def get_queryset(self):
        # Filtro global para incluir apenas os registros não excluídos
        return super().get_queryset().filter(excluido=False)

class AreaTrilhaManager(models.Manager):
    def get_queryset(self):
        # Filtro global para incluir apenas os registros não excluídos
        return super().get_queryset().filter(excluido=False)