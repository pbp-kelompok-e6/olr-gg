import json
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db import IntegrityError
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from berita.models import News 
from .models import ReadingList, ReadingListItem
from .forms import ReadingListForm
from users.models import CustomUser as User
from django.contrib.auth import get_user_model

User = get_user_model();

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

@login_required
def get_user_lists_ajax(request):
    """Mengembalikan daftar ReadingList milik user dalam format JSON."""
    user_lists = ReadingList.objects.filter(user=request.user).values('id', 'name')
    data = [{'id': str(list['id']), 'name': list['name']} for list in user_lists]
    return JsonResponse(data, safe=False)

def get_news_list_status(user, news_id):
    """Mengembalikan status berita (ada/tidak ada) di setiap list user."""
    # Ambil semua list user
    user_lists = ReadingList.objects.filter(user=user).values('id', 'name')
    
    # Ambil semua ReadingListItem untuk berita ini dalam list user
    items_in_list = ReadingListItem.objects.filter(
        list__user=user, 
        news__id=news_id
    ).values_list('list__id', flat=True)
    
    data = []
    # Konversi list['id'] ke string 
    items_in_list_str = [str(id) for id in items_in_list]
    for list_obj in user_lists:
        is_in_list = str(list_obj['id']) in items_in_list_str
        data.append({
            'id': str(list_obj['id']),
            'name': list_obj['name'],
            'is_in_list': is_in_list
        })
        
    return data

@login_required
def get_news_list_status_ajax(request, news_id):
    """API: Mengembalikan status berita di semua list user dalam format JSON."""
    try:
        # Cek apakah news_id valid (UUID)
        News.objects.get(id=news_id) 
    except News.DoesNotExist:
        return JsonResponse({"status": "ERROR", "message": "News not found."}, status=404)
    
    data = get_news_list_status(request.user, news_id)
    return JsonResponse(data, safe=False)

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
            # buat RENAME
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

@login_required
@require_POST
def add_to_list_ajax(request, news_id):
    try:
        # 1. Parsing data dari body POST request
        data = json.loads(request.body)
        list_id = data.get('list_id')
        if not list_id:
            return JsonResponse({"status": "ERROR", "message": "List ID is required."}, status=400)
        # 2. Ambil objek News dan List
        news = get_object_or_404(News, id=news_id)
        # Penting: Pastikan list tersebut dimiliki oleh user yang sedang login
        reading_list = get_object_or_404(ReadingList, id=list_id, user=request.user)
        # 3. Toggle Status
        item, created = ReadingListItem.objects.get_or_create(
            list=reading_list,
            news=news
        )
        if created:
            message = f"News berhasil ditambahkan ke list '{reading_list.name}'."
            status = "ADDED"
        else:
            # Jika sudah ada, hapus (Toggle)
            item.delete()
            message = f"News berhasil dihapus dari list '{reading_list.name}'."
            status = "REMOVED"
        
        return JsonResponse({"status": status, "message": message, "list_name": reading_list.name})

    except json.JSONDecodeError:
        return JsonResponse({"status": "ERROR", "message": "Invalid JSON format."}, status=400)
    except IntegrityError:
        return JsonResponse({"status": "ERROR", "message": "A database integrity error occurred."}, status=500)
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