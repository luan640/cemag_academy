from django.shortcuts import render,redirect,get_object_or_404
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

from .models import Livro,Rating,VisualizacaoLivro
from .forms import AddLivro,RatingForm

def calculate_media_rating_livro(id_livro):
    
    livro = get_object_or_404(Livro, pk=id_livro) # Livro.objects.all()
    
    ratings = livro.ratings.all()

    if ratings:
        media_rating = sum(r.score for r in ratings) / len(ratings)
    else:
        media_rating = 0 
    
    return media_rating

def list_livro(request):
    livros = Livro.objects.all()

    # Obtendo os IDs dos livros visualizados pelo usuário
    visualizacoes = VisualizacaoLivro.objects.filter(
        user=request.user  # Use o objeto Funcionario
    ).values_list('livro_id', flat=True)
    
    visualizacao_ids = set(visualizacoes)  # Converter para conjunto para eficiência
    
    for livro in livros:
        user_rating = livro.ratings.filter(user=request.user).first()
        ratings = livro.ratings.all()

        if ratings:
            media_ratings = sum(r.score for r in ratings) / len(ratings)
        else:
            media_ratings = 0 

        livro.media_ratings = media_ratings

        if user_rating:
            livro.user_rating = user_rating.score  # Score unitário do usuário
        else:
            livro.user_rating = None  # Nenhum score encontrado para este livro e usuário
    
    return render(request, 'livro_list.html', {
        'livros': livros,
        'visualizacoes': visualizacao_ids  # Passar IDs dos livros visualizados
    })


def livro_add(request):
    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        autor = request.POST.get('autor')
        idioma = request.POST.get('idioma')
        ano = request.POST.get('ano')
        arquivo_pdf = request.FILES.get('arquivo_pdf')
        capa = request.FILES.get('capa')

        livro = Livro(
            titulo=titulo,
            autor=autor,
            idioma=idioma,
            ano=ano,
            arquivo_pdf=arquivo_pdf,
            capa=capa,
            created_by=request.user
        )
        
        try:
            livro.full_clean()  # Validação dos campos
            livro.save()
            return redirect('list-livro')
        except ValidationError as e:
            return render(request, 'livro_list.html', {
                'form_errors': e.message_dict,
                'livros': Livro.objects.all()
            })

    return redirect('list-livro')

def registrar_visualizacao_livro(request):
    if request.method == 'POST':
        livro_id = request.POST.get('livro_id')

        try:
            livro = get_object_or_404(Livro, pk=livro_id)

            visualizacao = VisualizacaoLivro.objects.get(
                user=request.user,  # Use o objeto Funcionario
                livro=livro
            )

            visualizacao.delete()
            return JsonResponse({'status': 'desmarcado'})

        except VisualizacaoLivro.DoesNotExist:
            visualizacao = VisualizacaoLivro(
                user=request.user,  # Use o objeto Funcionario
                livro=livro
            )
            visualizacao.save()
            return JsonResponse({'status': 'marcado'})
        
@csrf_exempt
@login_required
def add_rating(request):
    if request.method == 'POST':
        livro_id = request.POST.get('livro_id')
        score = request.POST.get('rating')
        
        if not livro_id or not score:
            return JsonResponse({'success': False, 'message': 'Missing parameters'}, status=400)
        
        livro = get_object_or_404(Livro, pk=livro_id)
        rating, created = Rating.objects.get_or_create(user=request.user, livro=livro, defaults={'score': score})
        
        if not created:
            rating.score = score
            rating.save()
        
        # media = calculate_media_rating_livro(livro_id)
        
        return JsonResponse({'success': True,'rating': rating.score})

    return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=400)
