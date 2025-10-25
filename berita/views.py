from django.shortcuts import render, redirect, get_object_or_404
from berita.forms import newsForm
from berita.models import News
from main.views import login_required
from django.http import JsonResponse, HttpResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.html import strip_tags
from comments.models import Comments
from django.db.models import Avg
from rating.models import Rating

def show_news(request, id):
    news = get_object_or_404(News, pk=id)
    comments = Comments.objects.filter(news=news).select_related('user').order_by('-created_at')
    context = {
        'news': news,
        'comments': comments
    }
    return render(request, "news_detail.html", context)

@csrf_exempt
@require_POST
@login_required
def edit_news(request, id):
    news = get_object_or_404(News, pk=id, user=request.user)  # pastikan hanya user sendiri

    news.title = strip_tags(request.POST.get("title"))
    news.content = strip_tags(request.POST.get("content"))
    news.category = request.POST.get("category")
    news.thumbnail = request.POST.get("thumbnail")
    news.is_featured = request.POST.get("is_featured") == 'on'
    news.save()

    return HttpResponse(b"UPDATED", status=200)

@login_required(login_url='/login')
@csrf_exempt
def delete_news(request, id):
    if request.method == 'POST':
        try:
            news = News.objects.get(id=id, user=request.user)
            news.delete()
            return JsonResponse({"success": True})
        except News.DoesNotExist:
            return JsonResponse({"error": "News not found"}, status=404)
    return JsonResponse({"error": "Invalid request"}, status=400)

@csrf_exempt
@require_POST
@login_required
def create_news(request):
    title = strip_tags(request.POST.get("title")) # strip HTML tags!
    content = strip_tags(request.POST.get("content")) # strip HTML tags!
    category = request.POST.get("category")
    thumbnail = request.POST.get("thumbnail")
    is_featured = request.POST.get("is_featured") == 'on'  # checkbox handling
    user = request.user

    news_baru = News(
        title=title, 
        content=content,
        category=category,
        thumbnail=thumbnail,
        is_featured=is_featured,
        user=user
    )
    news_baru.save()

    return HttpResponse(b"CREATED", status=201)

def show_json(request):
    news = News.objects.all().select_related('user')
    data = []
    for item in news:
        # Get average rating for this news
        avg_rating = Rating.objects.filter(news=item).aggregate(Avg('rating'))['rating__avg']
        rating_count = Rating.objects.filter(news=item).count()
        
        data.append({
            'id': str(item.id),
            'title': item.title,
            'content': item.content,
            'category': item.category,
            'thumbnail': item.thumbnail if item.thumbnail else None,
            'is_featured': item.is_featured,
            'created_at': item.created_at.isoformat(),
            'news_views': getattr(item, 'news_views', 0),  # Safe access dengan default 0
            'user_id': str(item.user.id),
            'user_username': item.user.username,
            'average_rating': round(avg_rating, 1) if avg_rating else None,
            'rating_count': rating_count,
        })
    return JsonResponse(data, safe=False)

def show_json_by_id(request, news_id):
    try:
        news = News.objects.select_related('user').get(pk=news_id)
        data = {
            'id': str(news.id),
            'title': news.title,
            'content': news.content,
            'category': news.category,
            'thumbnail': news.thumbnail,
            'created_at': news.created_at.isoformat() if news.created_at else None,
            'is_featured': news.is_featured,
            'user_id': news.user_id,
            'user_username': news.user.username if news.user_id else None,
        }
        return JsonResponse(data)
    except News.DoesNotExist:
        return JsonResponse({'detail': 'Not found'}, status=404)
