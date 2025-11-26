import json
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from .models import ReadingList, ReadingListItem
from .forms import ReadingListForm
from users.models import CustomUser as User
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError
from berita.models import News

User = get_user_model()

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


def get_news_list_status(user, news_id):
    """Mengembalikan status berita (ada/tidak ada) di setiap list user."""
    user_lists = ReadingList.objects.filter(user=user).values('id', 'name')
    
    items_in_list = ReadingListItem.objects.filter(
        list__user=user, 
        news__id=news_id
    ).values_list('list__id', flat=True)
    
    data = []

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
        News.objects.get(id=news_id) 
    except News.DoesNotExist:
        return JsonResponse({"status": "ERROR", "message": "News not found."}, status=404)
    
    data = get_news_list_status(request.user, news_id)
    return JsonResponse(data, safe=False)

@login_required
def show_reading_lists(request):
    """Dashboard List Bacaan Pribadi (URL: /list/)"""
    get_or_create_default_list(request.user) 
    
    user_lists = ReadingList.objects.filter(user=request.user).prefetch_related('items__news')

    list_form = ReadingListForm()

    context = {
        'user_lists': user_lists,
        'list_form': list_form
    }
    return render(request, 'readinglist/list_dashboard.html', context)

@login_required
@require_POST
def add_to_list_ajax(request, news_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            list_id = data.get('list_id')
            if not list_id:
                return JsonResponse({"status": "ERROR", "message": "List ID is required."}, status=400)

            news = get_object_or_404(News, id=news_id)

            reading_list = get_object_or_404(ReadingList, id=list_id, user=request.user)

            item, created = ReadingListItem.objects.get_or_create(
                list=reading_list,
                news=news
            )
            if created:
                message = f"News berhasil ditambahkan ke list '{reading_list.name}'."
                status = "ADDED"
            else:
          
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
    return JsonResponse({"status": "ERROR", "message": "Method not allowed"}, status=405)

@require_POST
@login_required
def toggle_read_status_ajax(request, item_id):
    """Mengubah Status Baca Berita (Toggle is_read) (POST ke /toggle_read/{item_id}/)"""
    if request.method == 'POST':
        item = get_object_or_404(ReadingListItem, id=item_id, list__user=request.user)
        item.is_read = not item.is_read
        item.save()
        
        status = "sudah dibaca" if item.is_read else "belum dibaca"
        return JsonResponse({"status": "SUCCESS", "message": f"Status diubah menjadi '{status}'."}, status=200)
    return JsonResponse({"status": "ERROR", "message": "Method not allowed"}, status=405)

@login_required
@require_POST
def create_list(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body or "{}")
        except Exception:
            return JsonResponse({"message": "Invalid JSON body"}, status=400)

        name = (data.get("name") or "").strip()
        if not name:
            return JsonResponse({"message": "List name is required"}, status=400)
        if name.lower() == "favorites":
            return JsonResponse({"message": 'Name "Favorites" is reserved'}, status=400)

        rl = ReadingList.objects.create(user=request.user, name=name)
        return JsonResponse({
            "message": "List created",
            "list": {
                "id": str(rl.id),
                "name": rl.name,
                "items_count": rl.items.count(),
            }
        }, status=201)
    return JsonResponse({"message": "Method not allowed"}, status=405)

@login_required
@require_POST
def rename_list(request, list_id):
    if request.method == 'POST':
        rl = get_object_or_404(ReadingList, id=list_id, user=request.user)
        if rl.name == "Favorites":
            return JsonResponse({"message": "Favorites cannot be renamed"}, status=400)

        try:
            data = json.loads(request.body or "{}")
        except Exception:
            return JsonResponse({"message": "Invalid JSON body"}, status=400)

        new_name = (data.get("name") or "").strip()
        if not new_name:
            return JsonResponse({"message": "List name is required"}, status=400)
        if new_name.lower() == "favorites":
            return JsonResponse({"message": 'Name "Favorites" is reserved'}, status=400)

        rl.name = new_name
        rl.save(update_fields=["name"])
        return JsonResponse({
            "message": "List renamed",
            "list": {
                "id": str(rl.id),
                "name": rl.name,
            }
        })
    return JsonResponse({"message": "Method not allowed"}, status=405)

@login_required
@require_POST
def delete_list(request, list_id):
    if request.method == 'POST':
        rl = get_object_or_404(ReadingList, id=list_id, user=request.user)
        if rl.name == "Favorites":
            return JsonResponse({"message": "Favorites cannot be deleted"}, status=400)

        rl.delete()
        return JsonResponse({"message": "List deleted", "id": str(list_id)})
    return JsonResponse({"message": "Method not allowed"}, status=405)

@login_required
@require_POST
def toggle_read(request, item_id):
    if request.method == 'POST':
        item = get_object_or_404(ReadingListItem, id=item_id, list__user=request.user)
        item.is_read = not item.is_read
        item.save(update_fields=["is_read"])
        return JsonResponse({"success": True, "is_read": item.is_read})
    return JsonResponse({"success": False, "message": "Method not allowed"}, status=405)    