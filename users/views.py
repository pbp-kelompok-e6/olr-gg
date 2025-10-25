from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import CustomUserChangeForm, ProfilePictureForm, ReportUserForm
from django.shortcuts import get_object_or_404
from .models import CustomUser as User, Report
from django.contrib.auth import get_user_model
from django.templatetags.static import static 
from berita.models import News
from .forms import AdminUserUpdateForm

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
        form = ProfilePictureForm(request.POST, request.FILES, instance=request.user)
        
        if form.is_valid():
            user_instance = form.save()

            if user_instance.profile_picture:
                pic_url = user_instance.profile_picture.url
            else:
                pic_url = static('image/default_profile_picture.jpg') 

            return JsonResponse({
                'status': 'success', 
                'message': 'Profile picture berhasil di update.',
                'new_data': {
                    'full_name': f"{user_instance.first_name or ''} {user_instance.last_name or ''}".strip(),
                    'bio': user_instance.bio or "This user has not added a bio yet.",
                    'profile_picture_url': pic_url 
                }
            })
    
        else:

            errors = form.errors.as_json()
            return JsonResponse({'status': 'error', 'errors': errors}, status=400)
    
    form = ProfilePictureForm(instance=request.user)
    context = {
        'form': form
    }
    return render(request, 'change_pic.html', context)


@login_required(login_url='/login')
def report_user(request, id):
    try:
        usertarget = User.objects.get(id=id)
    except User.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'User not found.'}, status=404)

    if usertarget == request.user:
        return JsonResponse({'status': 'error', 'message': 'You cannot report yourself.'}, status=403)

    if request.method == 'POST':
        form = ReportUserForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.reporter = request.user
            report.reported_user = usertarget
            report.save()

            return JsonResponse({
                'status': 'success',
                'message': f'User {usertarget.username} berhasil dilaporkan.'
            })
        else:
            errors = form.errors.as_json()
            return JsonResponse({'status': 'error', 'errors': errors}, status=400)
    
    form = ReportUserForm()
    context = {
        'form': form,
        'usertarget': usertarget
    }
    return render(request, 'report_user.html', context)

def is_admin(user):
    """Helper function untuk decorator @user_passes_test"""
    return user.is_authenticated and (user.is_staff or user.is_superuser)

@user_passes_test(is_admin, login_url='/login')
def admin_dashboard(request):
    """
    Menampilkan halaman dashboard utama dengan list user dan report.
    """
    users = User.objects.all().order_by('username')
    reports = Report.objects.all().select_related('reporter', 'reported_user').order_by('-created_at')
    
    context = {
        'users': users,
        'reports': reports,
    }
    return render(request, 'admin_dashboard.html', context)

@user_passes_test(is_admin, login_url='/login')
def admin_edit_user(request, id):

    user_to_edit = get_object_or_404(User, id=id)
    
    if request.method == 'POST':
        # request.FILES sudah ada di sini, ini penting untuk gambar
        form = AdminUserUpdateForm(request.POST, request.FILES, instance=user_to_edit)
        
        if form.is_valid():
            user = form.save(commit=False)
            
            if request.POST.get('reset_picture') == 'true':
                # Hapus file gambar yang ada
                user.profile_picture = None
                
            user.save()

            if user.profile_picture:
                pic_url = user.profile_picture.url
            else:
                pic_url = static('image/default_profile_picture.jpg') 
            # -----------------------------------------------

            return JsonResponse({
                'status': 'success', 
                'message': f'Profil untuk {user.username} berhasil diupdate.',
                'new_profile_picture_url': pic_url
            })
        else:
            # Kirim error form sebagai JSON
            errors = form.errors.as_json()
            return JsonResponse({'status': 'error', 'errors': errors}, status=400)
    
    else:
        # Request GET standar, render halaman seperti biasa
        form = AdminUserUpdateForm(instance=user_to_edit)
    
    context = {
        'form': form,
        'user_to_edit': user_to_edit
    }
    return render(request, 'admin_edit_user.html', context)

@user_passes_test(is_admin, login_url='/login')
def admin_reset_strikes(request, id):
    """
    MODIFIKASI: Action (POST only, AJAX) untuk mereset strike user.
    Logika re-aktivasi ditangani oleh models.py
    """
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid method.'}, status=405)

    try:
        user_to_reset = get_object_or_404(User, id=id)
        user_to_reset.strikes = 0
        
        # Method save() di models.py kamu akan otomatis 
        # mengatur is_active = True karena strike < 3
        user_to_reset.save()
        
        # Kirim kembali data baru agar JavaScript bisa update UI
        return JsonResponse({
            'status': 'success',
            'message': f"Strikes untuk {user_to_reset.username} telah direset.",
            'user_id': user_to_reset.id,
            'new_strike_count': user_to_reset.strikes, # akan jadi 0
            'is_active': user_to_reset.is_active   # akan jadi True
        })
        
    except User.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'User not found.'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@user_passes_test(is_admin, login_url='/login')
def admin_delete_report(request, id):
    """
    MODIFIKASI: Menolak laporan (POST only, AJAX).
    Hanya menghapus laporan.
    """
    if request.method != 'POST':
        # Ubah error ke JSON
        return JsonResponse({'status': 'error', 'message': 'Invalid method.'}, status=405)
        
    report = get_object_or_404(Report, id=id)
    report.delete()
    
    # Ubah redirect ke JSON
    return JsonResponse({
        'status': 'success',
        'message': 'Laporan telah ditolak (dihapus).',
        'action': 'rejected'
    })

@user_passes_test(is_admin, login_url='/login')
def admin_accept_report(request, id):
    """
    BARU: Menerima laporan (POST only, AJAX).
    Memberi +1 strike dan menghapus laporan.
    """
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid method.'}, status=405)
    
    try:
        report = get_object_or_404(Report, id=id)
        user_to_strike = report.reported_user
        
        # 1. Tambah strike
        user_to_strike.strikes += 1
        user_to_strike.save() 
        # (models.py akan otomatis menonaktifkan user jika strike >= 3)
        
        report_message = f"Laporan terhadap {user_to_strike.username} diterima. Strike sekarang: {user_to_strike.strikes}."
        
        # 2. Hapus laporan
        report.delete()
        
        return JsonResponse({
            'status': 'success',
            'message': report_message,
            'action': 'accepted',
            'user_id': user_to_strike.id,
            'new_strike_count': user_to_strike.strikes,
            'is_active': user_to_strike.is_active
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
