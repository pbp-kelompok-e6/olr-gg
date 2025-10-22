# readinglist/views.py
import json
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db import IntegrityError
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

# Import models dan forms dari aplikasi yang bersangkutan
from main.models import News 
from .models import ReadingList, ReadingListItem
from .forms import ReadingListForm

# --- UTILITY FUNCTION ---
def get_or_create_default_list(user):
    """Mencari atau membuat list 'Favorites' default untuk pengguna."""
    list_name = "Favorites"
    list_obj, created = ReadingList.objects.get_or_create(
        user=user, 
        name=list_name,
        # Hanya gunakan ini untuk memastikan jika user tidak pernah mengganti namanya
        defaults={'name': list_name} 
    )
    return list_obj

# --- VIEW FUNGSI ---

@login_required
def show_reading_lists(request):
    """Dashboard List Bacaan Pribadi (URL: /list/)"""
    # Memastikan list default ada, terutama saat pengguna pertama kali mengakses dashboard
    get_or_create_default_list(request.user) 
    
    # Mengambil semua list pengguna, prefetch terkait item dan beritanya
    user_lists = ReadingList.objects.filter(user=request.user).prefetch_related('items__news')
    
    # Form untuk membuat list baru
    list_form = ReadingListForm()

    context = {
        'user_lists': user_lists,
        'list_form': list_form
    }
    return render(request, 'readinglist/list_dashboard.html', context)

@require_POST
@login_required
@csrf_exempt
def create_or_rename_list_ajax(request, list_id=None):
    """CRUD: Membuat List Baru (POST ke /create_or_rename/) atau Mengubah Nama List (POST ke /create_or_rename/{id}/)"""
    try:
        data = json.loads(request.body)
        form = ReadingListForm(data)

        if list_id:
            # Operasi RENAME
            list_obj = get_object_or_404(ReadingList, id=list_id, user=request.user)
            form = ReadingListForm(data, instance=list_obj) # Gunakan instance untuk update

        if form.is_valid():
            new_list = form.save(commit=False)
            new_list.user = request.user
            new_list.save()
            
            message = "List berhasil diubah namanya!" if list_id else "List baru berhasil dibuat!"
            return JsonResponse({"status": "SUCCESS", "message": message, "list_name": new_list.name, "list_id": new_list.id}, status=200)
        else:
            errors = dict(form.errors.items())
            return JsonResponse({"status": "ERROR", "message": "Input tidak valid.", "errors": errors}, status=400)

    except json.JSONDecodeError:
        return JsonResponse({"status": "ERROR", "message": "Format JSON tidak valid."}, status=400)
    except Exception as e:
        return JsonResponse({"status": "ERROR", "message": str(e)}, status=500)

@require_POST
@login_required
@csrf_exempt
def delete_list_ajax(request, list_id):
    """CRUD: Menghapus List (POST ke /delete/{id}/)"""
    list_obj = get_object_or_404(ReadingList, id=list_id, user=request.user)
    list_obj.delete()
    return JsonResponse({"status": "SUCCESS", "message": f"List '{list_obj.name}' berhasil dihapus."}, status=200)

@require_POST
@login_required
@csrf_exempt
def add_to_list_ajax(request, news_id):
    """CRUD: Menambah/Menghapus Berita dari List (POST ke /add_remove/{news_id}/)"""
    news = get_object_or_404(News, id=news_id)

    try:
        data = json.loads(request.body)
        list_id = data.get('list_id')
    except json.JSONDecodeError:
        return JsonResponse({"status": "ERROR", "message": "Format JSON tidak valid."}, status=400)
    
    # Tentukan list tujuan (default ke 'Favorites' jika tidak ada list_id)
    if not list_id:
        list_obj = get_or_create_default_list(request.user)
    else:
        list_obj = get_object_or_404(ReadingList, id=list_id, user=request.user)

    try:
        # Coba tambahkan item baru (CREATE)
        ReadingListItem.objects.create(list=list_obj, news=news)
        return JsonResponse({"status": "SUCCESS", "message": f"Berita berhasil ditambahkan ke '{list_obj.name}'."}, status=201)
    except IntegrityError:
        # Jika sudah ada, hapus (Toggle/DELETE)
        item = ReadingListItem.objects.get(list=list_obj, news=news)
        item.delete()
        return JsonResponse({"status": "SUCCESS", "message": f"Berita dihapus dari '{list_obj.name}'."}, status=200)
    except Exception as e:
        return JsonResponse({"status": "ERROR", "message": str(e)}, status=500)

@require_POST
@login_required
@csrf_exempt
def toggle_read_status_ajax(request, item_id):
    """Mengubah Status Baca Berita (Toggle is_read) (POST ke /toggle_read/{item_id}/)"""
    # Pastikan item_id milik pengguna yang sedang login
    item = get_object_or_404(ReadingListItem, id=item_id, list__user=request.user)
    
    # Toggle status
    item.is_read = not item.is_read
    item.save()
    
    status = "sudah dibaca" if item.is_read else "belum dibaca"
    return JsonResponse({"status": "SUCCESS", "message": f"Status diubah menjadi '{status}'."}, status=200)