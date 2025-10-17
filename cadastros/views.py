
import openpyxl
from django.db import transaction
from django.shortcuts import render, redirect,get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .forms import AddArea,AddFuncionario,AddSetor
from .models import Funcionario,Setor,Area,AreaTrilha
from users.models import CustomUser

import logging

logger = logging.getLogger('cadastros')

SETOR_AREA_MAP = {
    'USINAGEM': 'Produção',
    'PINTURA': 'Produção',
    'PCP': 'Administrativo',
    'EXPEDICAO': 'Produção',
    'MANUTENÇÃO': 'Produção', # Corrigido para 'Manutenção' se necessário
    'SOLDA': 'Produção',
    'SESMT': 'Administrativo',
    'COMPRAS': 'Administrativo',
    'CORTE/ESTAMP.': 'Produção',
    'PROTOTIPOS': 'Produção',
    'PROJETOS': 'Administrativo',
    'QUALIDADE': 'Produção',
    'MARKETING': 'Administrativo',
    'PORTARIA': 'Produção',
    'FORJARIA/TRAT. TERMI': 'Produção',
    'GESTAO INDUSTRIAL': 'Administrativo',
    'COMERCIAL': 'Administrativo',
    'FINANCEIRO': 'Administrativo',
    'GESTAO DE PESSOAS': 'Administrativo',
    'ALMOXARIFADO': 'Produção',
    'CONTABILIDADE': 'Administrativo',
    'CARPINTARIA': 'Produção',
    'TI - DESENVOLVIMENTO': 'Administrativo',
    'TI - MANUNTECAO - REDE': 'Produção'
}

@login_required
def funcionario_cadastro(request):
    if request.user.type == "ADM":
        if request.method == 'POST':
            form = AddFuncionario(request.POST)
            if form.is_valid():
                funcionario = form.save(commit=False)
                funcionario.created_by = request.user
                funcionario.save()
                messages.success(request, 'Funcionário adicionado com sucesso.')
                # Redireciona após o POST bem-sucedido
                return redirect('funcionarios')
            else:
                messages.error(request, 'Erro ao adicionar o funcionário. Verifique os dados e tente novamente.')
        
        # Se não for um POST ou o formulário não for válido, exibe o formulário
        form = AddFuncionario()
        funcionarios = Funcionario.objects.all()
        return render(request, 'funcionario/funcionarios.html', {
            'form': form,
            'funcionarios': funcionarios
        })
    else:
        return redirect('home')

@login_required
def funcionario_edit(request, pk):
    funcionario = get_object_or_404(Funcionario, pk=pk)
    if request.method == 'POST':
        form = AddFuncionario(request.POST, instance=funcionario)
        if form.is_valid():
            funcionario = form.save(commit=False)
            funcionario.save()
            form.save_m2m()  # Salva os campos ManyToMany após salvar o objeto principal
            messages.success(request, 'Funcionario editado com sucesso.')
            return redirect('funcionarios')
    else:
        form = AddFuncionario(instance=funcionario)
    return render(request, 'funcionario/funcionario_edit.html', {'form': form})

@login_required
def funcionario_delete(request, pk):
    funcionario = get_object_or_404(Funcionario,pk=pk)
    funcionario.excluido = True
    funcionario.save()

    messages.success(request, 'Funcionario excluído com sucesso.')

    return redirect('funcionarios')


@login_required
def setor_cadastro(request):
    if request.user.type == "ADM":
        setores = Setor.objects.filter(excluido=False)  # Filtra setores onde excluido é False
        if request.method == 'POST':
            form = AddSetor(request.POST)
            if form.is_valid():
                setor = form.save(commit=False)
                setor.created_by = request.user
                setor.save()
                messages.success(request, 'Setor adicionado com sucesso.')
                return redirect('setores')
        else:
            form = AddSetor()

        return render(request, 'setor/setores.html', {'form': form, 'setores': setores})
    else:
        return redirect('home')
    
@login_required
def setor_edit(request, pk):
    logger.debug(f"Edit setor: {pk}")
    setor = get_object_or_404(Setor, pk=pk)
    logger.debug(f"Found setor: {setor}")

    if request.method == 'POST':
        logger.debug(f"POST data: {request.POST}")
        form = AddSetor(request.POST, instance=setor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Setor editado com sucesso.')
            logger.debug(f"Setor {setor} editado com sucesso.")
            return redirect('setores')
        else:
            logger.debug(f"Form errors: {form.errors}")
    else:
        form = AddSetor(instance=setor)

    return render(request, 'setor/setor_edit.html', {'form': form})

@login_required
def setor_delete(request, pk):
    setor = get_object_or_404(Setor,pk=pk)
    setor.excluido = True
    setor.save()

    messages.success(request, 'Setor excluído com sucesso.')

    return redirect('setores')


@login_required
def area_cadastro(request):
    if request.user.type == "ADM":
        if request.method == 'POST':
            form = AddArea(request.POST)
            if form.is_valid():
                area = form.save(commit=False)
                area.created_by = request.user
                area.save()
                messages.success(request, 'Area adicionada com sucesso.')
                return redirect('areas')
            else:
                messages.error(request, "Essa área já existe", extra_tags='area')
        form = AddArea()
        areas=Area.objects.all()
        return render(request, 'area/areas.html', {'form': form,'areas':areas})
    else:
        return redirect('home')

@login_required
def area_edit(request, pk):
    area = get_object_or_404(Area, pk=pk)
    if request.method == 'POST':
        form = AddArea(request.POST, instance=area)
        if form.is_valid():
            area = form.save(commit=False)
            area.save()
            form.save_m2m()  # Salva os campos ManyToMany após salvar o objeto principal
            messages.success(request, 'Area editada com sucesso.')
            return redirect('areas')
    else:
        form = AddArea(instance=area)
    return render(request, 'area/area_edit.html', {'form': form})

@login_required
def area_delete(request, pk):
    area = get_object_or_404(Area,pk=pk)
    area.excluido = True
    area.save()

    messages.success(request, 'Area excluído com sucesso.')

    return redirect('areas')

@csrf_exempt
@transaction.atomic # Envolve toda a view em uma transação para garantir a consistência
def importar_funcionarios(request):
    if request.method != "POST":
        return JsonResponse({'error': 'Método não permitido'}, status=405)

    file = request.FILES.get('arquivo_excel')
    if not file:
        return JsonResponse({'error': 'Arquivo não enviado.'}, status=400)

    # --- 1. Leitura e Preparação Inicial (em memória) ---
    wb = openpyxl.load_workbook(file, read_only=True) # read_only=True é mais rápido
    ws = wb.active

    funcionarios_planilha = []
    setor_atual = None
    erros = []

    for row in ws.iter_rows(min_row=8, values_only=True): # values_only=True é mais rápido
        codigo, nome = row[0], row[1]

        if codigo and ' - ' in str(codigo) and '.' in str(codigo).split(' - ')[0]:
            setor_nome = str(codigo).split('-')[-1].strip().upper()
            setor_atual = setor_nome
            continue

        if codigo and nome and setor_atual:
            try:
                matricula_int = int(str(codigo).lstrip('0'))
            except (ValueError, TypeError):
                erros.append(f"Matrícula inválida: {codigo} ({nome}) - Setor: {setor_atual}")
                continue
            
            nome_parts = nome.strip().split()
            first_name = nome_parts[0]
            last_name = " ".join(nome_parts[1:]) if len(nome_parts) > 1 else ""
            
            funcionarios_planilha.append({
                'matricula': matricula_int,
                'nome': nome.strip(),
                'first_name': first_name,
                'last_name': last_name,
                'setor_nome': setor_atual,
            })

    if not funcionarios_planilha:
        return JsonResponse({'error': 'Nenhum funcionário válido encontrado na planilha.'}, status=400)

    # --- 2. Busca de Dados Existentes no DB (consultas otimizadas) ---
    matriculas_planilha = {f['matricula'] for f in funcionarios_planilha}
    
    setores_db = {s.nome.upper(): s for s in Setor.objects.filter(excluido=False)}
    
    # Usar select_related para buscar o usuário junto com o funcionário em uma única query
    funcionarios_db_map = {
        f.matricula: f for f in Funcionario.objects.select_related('user').filter(excluido=False)
    }
    
    users_db_map = {u.matricula: u for u in CustomUser.objects.filter(matricula__in=matriculas_planilha)}

    # --- 3. Processamento e Preparação das Listas para Bulk Operations (em memória) ---
    users_para_criar = []
    funcs_para_criar = []
    funcs_para_atualizar = []
    
    for f_data in funcionarios_planilha:
        matricula = f_data['matricula']
        setor = setores_db.get(f_data['setor_nome'].upper())
        if not setor:
            erros.append(f"Setor não encontrado: {f_data['setor_nome']} (Matrícula: {matricula})")
            continue

        func_existente = funcionarios_db_map.get(matricula)
        user_existente = users_db_map.get(matricula)
        user_para_associar = user_existente

        if not user_para_associar:
            user_para_associar = CustomUser(
                matricula=matricula,
                first_name=f_data['first_name'],
                last_name=f_data['last_name'],
                type='LEI',
                is_active=True,
                password=make_password(str(matricula))
            )
            users_para_criar.append(user_para_associar)
            users_db_map[matricula] = user_para_associar
        
        if func_existente:
            alterado = False
            if func_existente.nome != f_data['nome']:
                func_existente.nome = f_data['nome']
                alterado = True
            if func_existente.setor_id != setor.id:
                func_existente.setor = setor
                alterado = True
            if func_existente.excluido:
                func_existente.excluido = False
                alterado = True
            if not func_existente.user_id:
                func_existente.user = user_para_associar
                alterado = True
            
            if alterado:
                funcs_para_atualizar.append(func_existente)
        
        else:
            funcs_para_criar.append(Funcionario(
                matricula=matricula,
                nome=f_data['nome'],
                setor=setor,
                user=user_para_associar,
                excluido=False
            ))

    
    if users_para_criar:
        CustomUser.objects.bulk_create(users_para_criar)
        users_criados_map = {u.matricula: u for u in CustomUser.objects.filter(matricula__in={u.matricula for u in users_para_criar})}
        users_db_map.update(users_criados_map)
    
    for func in funcs_para_criar:
        if not func.user.pk: 
            func.user = users_db_map[func.matricula]

    for func in funcs_para_atualizar:
        if not func.user.pk:
            func.user = users_db_map[func.matricula]

    if funcs_para_criar:
        Funcionario.objects.bulk_create(funcs_para_criar)
    
    if funcs_para_atualizar:
        Funcionario.objects.bulk_update(
            funcs_para_atualizar, 
            ['nome', 'setor', 'excluido', 'user']
        )
    
    matriculas_db = set(funcionarios_db_map.keys())
    matriculas_para_desativar = matriculas_db - matriculas_planilha
    
    query_desativacao = Funcionario.objects.filter(matricula__in=matriculas_para_desativar)
    query_desativacao = query_desativacao.exclude(user__type='ADM') 
    desativados_count = query_desativacao.update(excluido=True)


    return JsonResponse({
        'status': 'Importação concluída.',
        'adicionados': len(funcs_para_criar),
        'atualizados': len(funcs_para_atualizar),
        'desativados': desativados_count,
        'novos_usuarios_criados': len(users_para_criar),
        'erros': erros,
    }, status=200)