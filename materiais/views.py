from django.shortcuts import render, redirect,get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import Pasta,Material
from .forms import AddPasta,AddMaterial
from cadastros.models import Funcionario

@login_required
def pastas_add(request):
    if request.method == 'POST':
        form = AddPasta(request.POST)
        if form.is_valid():
            pasta = form.save(commit=False)
            pasta.created_by = request.user
            pasta.save()
            form.save_m2m()  # Salva os campos ManyToMany após salvar o objeto principal
            messages.success(request, 'Pasta adicionada com sucesso.')
            return redirect('list-pasta')
    else:
        form = AddPasta()
    return render(request, 'pastas/pasta_add.html', {'form': form})

@login_required
def pastas_list(request):

    if request.user.is_staff:
        # Se o usuário for um membro da equipe (staff), ele tem acesso a todas as pastas
        pastas = Pasta.objects.all()
    else:
        setor_do_usuario_object = Funcionario.objects.get(matricula=request.user)

        setor_do_usuario = setor_do_usuario_object.setor.first()
        
        # Obtendo todas as pastas disponíveis
        pastas_disponiveis = Pasta.objects.all()

        # Filtrando as pastas disponíveis pelo setor do usuário logado
        pastas = pastas_disponiveis.filter(setores=setor_do_usuario)

    return render(request, 'pastas/pasta_list.html', {'pastas': pastas})

@login_required
def pastas_detail(request, pk):
    pasta = get_object_or_404(Pasta, pk=pk)
    is_staff = request.user.is_staff

    if is_staff or \
       request.user.setores.filter(pk__in=pasta.setores.all()).exists() or \
       pasta.funcionarios.filter(matricula=request.user.matricula).exists():
        # Se o usuário for um membro da equipe (staff) OU
        # Se o setor do usuário estiver dentro dos setores da pasta OU
        # Se a matrícula do usuário estiver na lista de funcionários da pasta
        materiais = Material.objects.filter(pasta=pasta)
        return render(request, 'pastas/pasta_detail.html', {
            'pasta': pasta,
            'materiais': materiais,
        })
    else:
        return render(request, '403.html')

@login_required
def pasta_edit(request, pk):
    pasta = get_object_or_404(Pasta, pk=pk)
    if request.method == 'POST':
        form = AddPasta(request.POST, instance=pasta)
        if form.is_valid():
            pasta = form.save(commit=False)
            pasta.save()
            form.save_m2m()  # Salva os campos ManyToMany após salvar o objeto principal
            messages.success(request, 'Pasta editada com sucesso.')
            return redirect('list-pasta')
    else:
        form = AddPasta(instance=pasta)
    return render(request, 'pastas/pasta_edit.html', {'form': form})

@login_required
def pasta_delete(request, pk):
    pasta = get_object_or_404(Pasta, pk=pk)
    pasta.delete()

    messages.success(request, 'Pasta excluída com sucesso.')

    return redirect('list-pasta')

@login_required
def material_add(request):
    if request.method == 'POST':
        form = AddMaterial(request.POST, request.FILES)  # Inclua request.FILES
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

@login_required
def material_add_in_pasta(request, pk):
    pasta = get_object_or_404(Pasta, pk=pk)

    if request.method == 'POST':
        form = AddMaterial(request.POST, request.FILES)
        if form.is_valid():
            material = form.save(commit=False)
            material.pasta = pasta  # Define a pasta associada
            material.created_by = request.user
            material.save()
            return redirect('detail-pasta', pk=pasta.pk)
    else:
        form = AddMaterial()

    return render(request, 'materiais/material_add.html', {
        'form': form,
        'pasta': pasta
    })

@login_required
def material_list(request):
    materiais = Material.objects.all()
    return render(request, 'materiais/material_list.html', {
        'materiais': materiais
    })

@login_required
def material_detail(request, pk):
    material = get_object_or_404(Material, pk=pk)
    return render(request, 'materiais/material_detail.html', {
        'material': material
    })

@login_required
def material_edit(request, pk_material, pk_pasta):
    material = get_object_or_404(Material, pk=pk_material)
    pasta = get_object_or_404(Pasta, pk=pk_pasta)
    
    # Verificar se o material pertence à pasta
    if material.pasta != pasta:
        messages.error(request, 'Material não pertence à pasta especificada.')
        return redirect('detail-pasta', pk=pasta.pk)

    if request.method == 'POST':
        form = AddMaterial(request.POST, request.FILES, instance=material)
        if form.is_valid():
            material = form.save(commit=False)
            material.pasta = pasta  # Garante que a pasta está sendo corretamente atribuída
            material.save()
            form.save_m2m()  # Salva os campos ManyToMany após salvar o objeto principal
            messages.success(request, 'Material editado com sucesso.')
            return redirect('detail-pasta', pk=pasta.pk)
        else:
            messages.error(request, 'Erro ao editar o material. Verifique os dados informados.')
    else:
        form = AddMaterial(instance=material)
    
    return render(request, 'materiais/material_edit.html', {'form': form, 'material': material, 'pasta': pasta})
