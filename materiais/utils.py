from materiais.models import Pasta,Material,Visualizacao
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet

class ProgressoTrilha:

    def __init__(self, funcionario, pastas):
        self.funcionario = funcionario
        self.pastas = pastas

    def calcular_progresso_pasta(self, pasta):
        materiais_pasta = Material.objects.filter(pasta=pasta)
        visualizacoes_pasta = Visualizacao.objects.filter(funcionario=self.funcionario, material__in=materiais_pasta)
        
        total_materiais = materiais_pasta.count()
        total_visualizados = visualizacoes_pasta.count()

        if total_materiais > 0:
            progresso = (total_visualizados / total_materiais) * 100
        else:
            progresso = 0

        return progresso

    def calcular_progresso_trilhas(self):
    # Otimizar utilizando agregações e cálculos no banco de dados, se possível
        progresso_pasta = {pasta.nome: self.calcular_progresso_pasta(pasta) for pasta in self.pastas}
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