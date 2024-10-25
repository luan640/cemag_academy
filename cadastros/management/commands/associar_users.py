from django.core.management.base import BaseCommand
from cadastros.models import Funcionario, CustomUser

class Command(BaseCommand):
    help = 'Associa usuários a funcionários com base na matrícula.'

    def handle(self, *args, **kwargs):
        # Obtém todos os funcionários que ainda não têm um user associado
        funcionarios = Funcionario.objects.filter(user__isnull=True)

        for funcionario in funcionarios:
            try:
                # Busca um CustomUser com a mesma matrícula do funcionário
                user = CustomUser.objects.get(matricula=funcionario.matricula)

                # Associa o CustomUser ao funcionário
                funcionario.user = user
                funcionario.save()
                print(f"Usuário {user} associado ao funcionário {funcionario.nome}.")
            except CustomUser.DoesNotExist:
                print(f"Nenhum usuário encontrado para a matrícula {funcionario.matricula}.")
            except Exception as e:
                print(f"Erro ao associar usuário para {funcionario.nome}: {e}")
