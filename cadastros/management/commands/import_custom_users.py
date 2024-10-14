import pandas as pd
from django.core.management.base import BaseCommand
from cadastros.models import CustomUser  # Importe o CustomUser do seu projeto

class Command(BaseCommand):
    help = 'Importa usuários a partir de um arquivo CSV para o banco de dados, verificando matrículas duplicadas e atualizando a senha com a matrícula'

    def handle(self, *args, **kwargs):
        # Carrega o arquivo CSV
        file_path = 'data-1727895201075.csv'  # Caminho do arquivo carregado
        data = pd.read_csv(file_path, delimiter=",", encoding="utf-8")

        for _, row in data.iterrows():
            try:
                # Verifica se a matrícula e o nome existem no CSV antes de criar o usuário
                matricula = row['matricula']
                nome_completo = row['nome']

                if pd.notna(matricula) and pd.notna(nome_completo):
                    # Separa o nome completo em first_name e last_name
                    nome_partes = nome_completo.split()
                    first_name = nome_partes[0]  # Primeiro nome
                    last_name = ' '.join(nome_partes[1:])  # Restante do nome

                    # Tenta buscar o usuário pela matrícula
                    user, created = CustomUser.objects.get_or_create(
                        matricula=int(matricula),
                        defaults={
                            'first_name': first_name,
                            'last_name': last_name,
                            'email': '',  # Deixe o email em branco
                            'type': 'LEI',
                            'is_active': True
                        }
                    )

                    # Atualiza a senha com a matrícula
                    user.set_password(str(matricula))
                    user.save()

                    if created:
                        print(f"Usuário {first_name} {last_name} inserido e senha configurada com sucesso.")
                    else:
                        print(f"Usuário {first_name} {last_name} já existia, senha atualizada para a matrícula.")
                else:
                    print(f"Dados insuficientes para criar usuário: {row}")
            except Exception as e:
                print(f"Erro ao processar usuário com matrícula {matricula}: {e}")
