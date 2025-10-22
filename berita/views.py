from django.shortcuts import render, redirect, get_object_or_404
from berita.forms import beritaForm
from berita.models import Berita
from main.views import login_required
from django.http import JsonResponse, HttpResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.html import strip_tags

@login_required(login_url='/login')
def show_berita(request, id):
    berita = get_object_or_404(Berita, pk=id)

    context = {
        'berita': berita
    }

    return render(request, "berita_detail.html", context)

@csrf_exempt
@require_POST
@login_required
def edit_berita(request, id):
    berita = get_object_or_404(Berita, pk=id, user=request.user)  # pastikan hanya user sendiri

    berita.title = strip_tags(request.POST.get("title"))
    berita.content = strip_tags(request.POST.get("content"))
    berita.category = request.POST.get("category")
    berita.thumbnail = request.POST.get("thumbnail")
    berita.is_featured = request.POST.get("is_featured") == 'on'
    berita.save()

    return HttpResponse(b"UPDATED", status=200)

@login_required(login_url='/login')
@csrf_exempt
def delete_berita(request, id):
    if request.method == 'DELETE':
        try:
            berita = Berita.objects.get(id=id, user=request.user)
            berita.delete()
            return JsonResponse({"success": True})
        except Berita.DoesNotExist:
            return JsonResponse({"error": "Berita not found"}, status=404)
    return JsonResponse({"error": "Invalid request"}, status=400)

@csrf_exempt
@require_POST
def add_berita(request):
    title = strip_tags(request.POST.get("title")) # strip HTML tags!
    content = strip_tags(request.POST.get("content")) # strip HTML tags!
    category = request.POST.get("category")
    thumbnail = request.POST.get("thumbnail")
    is_featured = request.POST.get("is_featured") == 'on'  # checkbox handling
    user = request.user

    berita_baru = Berita(
        title=title, 
        content=content,
        category=category,
        thumbnail=thumbnail,
        is_featured=is_featured,
        user=user
    )
    berita_baru.save()

    return HttpResponse(b"CREATED", status=201)
