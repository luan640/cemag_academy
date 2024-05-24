from django.shortcuts import render, redirect
from .models import Pasta
from .forms import AddPasta

def pastas_add(request):
    if request.method == 'POST':
        form = AddPasta(request.POST)
        if form.is_valid():
            pasta = form.save(commit=False)
            pasta.created_by = request.user
            pasta.save()
            return redirect('list-pastas')
    else:
        form = AddPasta()
    return render(request, 'pasta_add.html', {
        'form': form,
    })

def pastas_list(request):
    pastas = Pasta.objects.all()
    return render(request, 'pasta_list.html', {
        'pastas': pastas
    })

def pastas_detail(request, pk):
    pasta = Pasta.objects.get(pk=pk)
    return render(request, 'pasta_detail.html', {
        'pasta': pasta
    })
