
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .forms import AddArea,AddFuncionario,AddSetor
from .models import Funcionario,Setor,Area,AreaTrilha

import logging

logger = logging.getLogger('cadastros')

@login_required
def funcionario_cadastro(request):
    if request.user.type == "ADM":
        if request.method == 'POST':
            form = AddFuncionario(request.POST)
            if form.is_valid():
                funcionario = form.save(commit=False)
                funcionario.created_by = request.user
                funcionario.save()
                messages.success(request, 'Funcionario adicionado com sucesso.')
                return redirect('funcionarios')
        else:
            form = AddFuncionario()
            funcionarios = Funcionario.objects.all()

        return render(request,
                    'funcionario/funcionarios.html', {
                    'form': form,
                    'funcionarios':funcionarios})
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
    funcionario.delete()

    messages.success(request, 'Funcionario excluído com sucesso.')

    return redirect('funcionarios')


@login_required
def setor_cadastro(request):
    if request.user.type == "ADM":
        setores = Setor.objects.all()  # Consulta fora do bloco if/else
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
    setor.delete()

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
    area.delete()

    messages.success(request, 'Area excluído com sucesso.')

    return redirect('areas')