from materiais.models import Pasta,Material,Visualizacao

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