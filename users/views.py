from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import CustomUserChangeForm, ProfilePictureForm
from django.shortcuts import get_object_or_404
from .models import CustomUser as User
from django.contrib.auth import get_user_model
from django.templatetags.static import static 
from berita.models import News

User = get_user_model()

@login_required(login_url='/login')
def edit_profile(request):
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, request.FILES, instance=request.user)
        
        if form.is_valid():
            user_instance = form.save() 
            
            if user_instance.profile_picture:
                pic_url = user_instance.profile_picture.url
            else:
                pic_url = static('image/default_profile_picture.jpg') 

            return JsonResponse({
                'status': 'success', 
                'message': 'Profile berhasil di update.',
                'new_data': {
                    'full_name': f"{user_instance.first_name or ''} {user_instance.last_name or ''}".strip(),
                    'bio': user_instance.bio or "This user has not added a bio yet.",
                    'profile_picture_url': pic_url
                }
            })
    
        else:
            errors = form.errors.as_json()
            return JsonResponse({'status': 'error', 'errors': errors}, status=400)
    form = CustomUserChangeForm(instance=request.user)
    context = {
        'form': form
    }

    return render(request, 'edit_profile.html', context) 

def show_profile(request, id):
    target_user = get_object_or_404(User, id=id)

    if request.user.is_authenticated and target_user == request.user:
        is_owner = True
    else:
        is_owner = False

    context = {
        'usertarget': target_user,
        'is_owner': is_owner
    }

    return render(request, 'show_profile.html', context)

def load_news(request, id):
    target_user = get_object_or_404(User, id=id)
    news_list = News.objects.filter(user=target_user).order_by('-created_at')

    context = {
        'news_list': news_list,
    }

    return render(request, 'user_news_list.html', context)

@login_required(login_url='/login')
def change_profile_pic(request):
    if request.method == 'POST':
        # Gunakan form baru kita
        form = ProfilePictureForm(request.POST, request.FILES, instance=request.user)
        
        if form.is_valid():
            user_instance = form.save()
            
            # Logika untuk mendapatkan URL gambar (sama seperti di view edit_profile Anda)
            if user_instance.profile_picture:
                pic_url = user_instance.profile_picture.url
            else:
                pic_url = static('image/default_profile_picture.jpg') 

            # Kirim JSON response yang SAMA PERSIS dengan view edit_profile Anda
            # Ini penting agar JavaScript Anda bisa memprosesnya
            return JsonResponse({
                'status': 'success', 
                'message': 'Profile picture berhasil di update.',
                'new_data': {
                    # Kita tetap kirim data ini agar JS tidak error
                    'full_name': f"{user_instance.first_name or ''} {user_instance.last_name or ''}".strip(),
                    'bio': user_instance.bio or "This user has not added a bio yet.",
                    # Ini data yang akan di-update
                    'profile_picture_url': pic_url 
                }
            })
    
        else:
            # Kirim error jika form tidak valid
            errors = form.errors.as_json()
            return JsonResponse({'status': 'error', 'errors': errors}, status=400)
    
    # Untuk GET request, tampilkan form
    form = ProfilePictureForm(instance=request.user)
    context = {
        'form': form
    }
    # Kita akan buat template modal baru
    return render(request, 'change_pic.html', context)