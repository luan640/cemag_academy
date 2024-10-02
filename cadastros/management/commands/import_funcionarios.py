import pandas as pd
from django.core.management.base import BaseCommand
from cadastros.models import Funcionario, Setor, Area  # Importe os modelos corretos

class Command(BaseCommand):
    help = 'Importa os funcionários de um arquivo CSV para o banco de dados'

    def handle(self, *args, **kwargs):
        # Carrega o arquivo CSV
        file_path = 'data-1727895201075.csv'  # Caminho do arquivo carregado
        data = pd.read_csv(file_path, delimiter=",", encoding="utf-8")

        # Define os setores que pertencem à área Administrativa
        setores_administrativos = [
            'PCP', 'SESMT', 'COMPRAS', 'T.I - MANUTENCAO - REDE', 'T.I - DESENVOLVIMENTO', 
            'PROJETOS', 'COMERCIAL', 'GESTAO DE PESSOAS', 'CONTABILIDADE', 'GESTAO INDUSTRIAL', 
            'MARKETING'
        ]

        # Obtém ou cria as áreas no banco de dados
        area_administrativa, _ = Area.objects.get_or_create(nome='Administrativo')
        area_producao, _ = Area.objects.get_or_create(nome='Produção')

        for _, row in data.iterrows():
            try:
                setor_nome = row['setor'].strip()

                # Define a área correta para cada setor
                if setor_nome in setores_administrativos:
                    area = area_administrativa
                else:
                    area = area_producao

                # Obtém ou cria o setor com a área correta
                setor, _ = Setor.objects.get_or_create(nome=setor_nome, area=area)

                # Cria o funcionário e associa ao setor
                Funcionario.objects.create(
                    matricula=int(row['matricula']),
                    nome=row['nome'],
                    setor=setor
                )
                print(f"Funcionário {row['nome']} inserido com sucesso.")
            except Exception as e:
                print(f"Erro ao inserir {row['nome']}: {e}")
