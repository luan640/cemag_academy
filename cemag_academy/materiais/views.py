from django.shortcuts import render, redirect,get_object_or_404
from django.contrib import messages

from .models import Pasta,Material
from .forms import AddPasta,AddMaterial

def pastas_add(request):
    if request.method == 'POST':
        form = AddPasta(request.POST)
        if form.is_valid():
            pasta = form.save(commit=False)
            pasta.created_by = request.user
            pasta.save()
            return redirect('list-pasta')
    else:
        form = AddPasta()
    return render(request, 'pastas/pasta_add.html', {
        'form': form,
    })

def pastas_list(request):
    pastas = Pasta.objects.all()
    return render(request, 'pastas/pasta_list.html', {
        'pastas': pastas
    })

def pastas_detail(request, pk):
    pasta = get_object_or_404(Pasta, pk=pk)
    return render(request, 'pastas/pasta_detail.html', {
        'pasta': pasta
    })

def pasta_edit(request, pk):
    pasta = get_object_or_404(Pasta, pk=pk)
    if request.method == 'POST':
        form = AddPasta(request.POST, instance=pasta)
        if form.is_valid():
            form.save()
            messages.success(request, 'Pasta updated successfully.')
            return redirect('list-pasta')
    else:
        form = AddPasta(instance=pasta)
    return render(request, 'pastas/pasta_edit.html', {
        'form': form,
    })

def pasta_delete(request, pk):
    pasta = get_object_or_404(Pasta, pk=pk)
    pasta.delete()

    messages.success(request, 'Pasta excluída com sucesso.')

    return redirect('list-pasta')

def material_add(request):
    if request.method == 'POST':
        form = AddMaterial(request.POST)
        if form.is_valid():
            material = form.save(commit=False)
            material.created_by = request.user
            material.save()
            return redirect('list-material')
    else:
        form = AddMaterial()
    return render(request, 'materiais/material_add.html', {
        'form': form,
    })

def material_list(request):
    materiais = Material.objects.all()
    return render(request, 'materiais/material_list.html', {
        'materiais': materiais
    })

def material_detail(request, pk):
    material = get_object_or_404(Material, pk=pk)
    return render(request, 'materiais/material_detail.html', {
        'material': material
    })