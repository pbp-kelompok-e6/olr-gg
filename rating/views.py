from django.shortcuts import render

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from berita.models import News
from .models import Rating
from .forms import ReviewForm
from django.http import HttpResponseForbidden, JsonResponse

def get_ratings_json(request, news_id):
    ratings = Rating.objects.filter(news_id=news_id)
    data = [
        {
            'id': rating.id,
            'rating': rating.rating,
            'review': rating.review,
            'created_at': rating.created_at.isoformat(),
            'user_username': rating.user.username,
            'can_edit': request.user == rating.user,
        }
        for rating in ratings
    ]
    return JsonResponse(data, safe=False)

@csrf_exempt
def add_rating(request, news_id):
    if not request.user.is_authenticated:
        return JsonResponse({
            'status': 'error',
            'message': 'Authentication required'
        }, status=401)
    
    if request.method == 'POST':
        news = get_object_or_404(News, id=news_id)

        # Cek apakah user pernah mereview news atau belum
        existing_review = Rating.objects.filter(news=news, user=request.user).first()
        
        if existing_review:
            return JsonResponse({
                'status': 'error',
                'message': "Anda sudah memberikan review untuk news ini"
            }, status=400)

        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.news = news
            review.user = request.user
            review.save()
            
            return JsonResponse({
                'status': 'success',
                'message': "Review berhasil ditambahkan",
                'rating': {
                    'id': review.id,
                    'rating': review.rating,
                    'review': review.review,
                    'created_at': review.created_at.isoformat(),
                    'user_username': review.user.username,
                }
            })
        return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)

@csrf_exempt
def delete_rating(request, rating_id):
    if not request.user.is_authenticated:
        return JsonResponse({
            'status': 'error',
            'message': 'Authentication required'
        }, status=401)
    
    if request.method in ['DELETE', 'POST']:  # Support both DELETE and POST
        rating = get_object_or_404(Rating, id=rating_id)
        # Cek apakah user pemilik dari rating ini
        if rating.user != request.user:
            return JsonResponse({
                'status': 'error',
                'message': "Kamu tidak memiliki izin untuk menghapus rating ini."
            }, status=403)
        
        rating.delete()
        return JsonResponse({
            'status': 'success',
            'message': "Rating berhasil dihapus"
        })

@csrf_exempt
def edit_rating(request, rating_id):
    if not request.user.is_authenticated:
        return JsonResponse({
            'status': 'error',
            'message': 'Authentication required'
        }, status=401)
    
    rating = get_object_or_404(Rating, id=rating_id)
    
    if rating.user != request.user:
        return JsonResponse({
            'status': 'error',
            'message': "Kamu tidak memiliki izin untuk mengedit rating ini."
        }, status=403)

    if request.method in ['PUT', 'POST']:  # Support both PUT and POST
        import json
        from django.http import QueryDict
        
        # Parse data from request body
        if request.method == 'PUT':
            put_data = QueryDict(request.body)
            form = ReviewForm(put_data, instance=rating)
        else:  # POST
            form = ReviewForm(request.POST, instance=rating)
            
        if form.is_valid():
            rating = form.save()
            return JsonResponse({
                'status': 'success',
                'message': "Rating berhasil diperbarui",
                'rating': {
                    'id': rating.id,
                    'rating': rating.rating,
                    'review': rating.review,
                    'created_at': rating.created_at.isoformat(),
                    'user_username': rating.user.username,
                }
            })
        return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)