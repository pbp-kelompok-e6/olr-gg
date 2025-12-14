from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.csrf import csrf_exempt
from rating.models import Rating
from .forms import CustomUserChangeForm, ProfilePictureForm, ReportUserForm
from django.shortcuts import get_object_or_404
from .models import CustomUser as User, Report, WriterRequest
from django.contrib.auth import get_user_model
from django.templatetags.static import static 
from berita.models import News
from .forms import AdminUserUpdateForm, WriterRequestForm
from django.db.models import Q,  Avg

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

@csrf_exempt
@login_required(login_url='/login')
def edit_profile_flutter(request):
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
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('type') == 'json':
        if target_user.profile_picture:
            pic_url = target_user.profile_picture.url
        else:
            pic_url = static('image/default_profile_picture.jpg')

        return JsonResponse({
            'status': 'success',
            'data': {
                'id': target_user.id,
                'username': target_user.username,
                'full_name': f"{target_user.first_name or ''} {target_user.last_name or ''}".strip(),
                'bio': target_user.bio,
                'role': target_user.role,     
                'strikes': target_user.strikes,
                'date_joined': target_user.date_joined.strftime('%Y-%m-%d'),
                'profile_picture_url': pic_url,
                'is_owner': request.user.is_authenticated and target_user == request.user
            }
        })

    if request.user.is_authenticated and target_user == request.user:
        is_owner = True
    else:
        is_owner = False

    context = {
        'usertarget': target_user,
        'is_owner': is_owner
    }

    return render(request, 'show_profile.html', context)

def load_news(request):
    user_id = request.GET.get('id')
    target_user = get_object_or_404(User, id=user_id)
    
    news_list = News.objects.filter(user=target_user).order_by('-created_at')

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('type') == 'json':
        data = []
        for news in news_list:
            avg_rating = Rating.objects.filter(news=news).aggregate(Avg('rating'))['rating__avg']
            rating_count = Rating.objects.filter(news=news).count()
            # Handle thumbnail
            thumb_url = ""
            if news.thumbnail:
                thumb_url = news.thumbnail.url
            else:
                thumb_url = static('image/default_news.jpg')

            item = {
                'id': news.id,
                'title': news.title,
                'content': news.content,
                'category': news.category,
                'category_display': news.get_category_display(),
                'thumbnail': thumb_url,
                'created_at': news.created_at.isoformat(),
                'is_featured': news.is_featured,
                'user_id': str(news.user.id),
                'user_username': news.user.username,
                'average_rating': round(avg_rating, 1) if avg_rating else None,
                'rating_count': rating_count,
            }
            data.append(item)
            
        return JsonResponse({
            'status': 'success',
            'news_list': data
        })

    context = {
        'news_list': news_list,
    }
    return render(request, 'user_news_list.html', context)

@csrf_exempt
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

@csrf_exempt
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
    return user.is_authenticated and (user.is_staff or user.is_superuser)

@csrf_exempt
@user_passes_test(is_admin, login_url='/login')
def admin_dashboard(request):
    users = User.objects.all().order_by('username')
    reports = Report.objects.all().select_related('reporter', 'reported_user').order_by('-created_at')
    writer_requests = WriterRequest.objects.filter(status='pending').select_related('user').order_by('created_at')

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('type') == 'json':
        users_data = []
        for user in users:
            pic_url = user.profile_picture.url if user.profile_picture else static('image/default_profile_picture.jpg')
            users_data.append({
                'id': user.id,
                'username': user.username,
                'full_name': f"{user.first_name or ''} {user.last_name or ''}".strip(),
                'role': user.role,
                'is_active': user.is_active,
                'strikes': user.strikes,
                'is_superuser': user.is_superuser,
                'profile_picture_url': pic_url,
            })
        
        reports_data = []
        for report in reports:
             reports_data.append({
                'id': report.id,
                'created_at': report.created_at.strftime('%d %b %Y, %H:%M'),
                'reporter_username': report.reporter.username,
                'reported_username': report.reported_user.username,
                'reported_user_id': report.reported_user.id,
                'reason': report.reason,
             })

        requests_data = []
        for req in writer_requests:
            requests_data.append({
                'id': req.id,
                'created_at': req.created_at.strftime('%d %b %Y, %H:%M'),
                'username': req.user.username,
                'user_id': req.user.id,
                'reason': req.reason,
            })

        return JsonResponse({
            'status': 'success',
            'users': users_data,
            'reports': reports_data,
            'writer_requests': requests_data
        })

    context = {
        'users': users,
        'reports': reports,
        'writer_requests': writer_requests,
    }
    return render(request, 'admin_dashboard.html', context)

@csrf_exempt
@user_passes_test(is_admin, login_url='/login')
def admin_edit_user(request, id):

    user_to_edit = get_object_or_404(User, id=id)
    
    if request.method == 'POST':

        form = AdminUserUpdateForm(request.POST, request.FILES, instance=user_to_edit)
        
        if form.is_valid():
            user = form.save(commit=False)
            
            if request.POST.get('reset_picture') == 'true':
                user.profile_picture = None
                
            user.save()

            if user.profile_picture:
                pic_url = user.profile_picture.url
            else:
                pic_url = static('image/default_profile_picture.jpg') 

            return JsonResponse({
                'status': 'success', 
                'message': f'Profil untuk {user.username} berhasil diupdate.',
                'new_profile_picture_url': pic_url
            })
        else:
            errors = form.errors.as_json()
            return JsonResponse({'status': 'error', 'errors': errors}, status=400)
    
    else:
        form = AdminUserUpdateForm(instance=user_to_edit)
    
    context = {
        'form': form,
        'user_to_edit': user_to_edit
    }
    return render(request, 'admin_edit_user.html', context)

@csrf_exempt
@user_passes_test(is_admin, login_url='/login')
def admin_reset_strikes(request, id):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid method.'}, status=405)

    try:
        user_to_reset = get_object_or_404(User, id=id)
        user_to_reset.strikes = 0

        user_to_reset.save()
        
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

@csrf_exempt
@user_passes_test(is_admin, login_url='/login')
def admin_delete_report(request, id):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid method.'}, status=405)
        
    report = get_object_or_404(Report, id=id)
    report.delete()

    return JsonResponse({
        'status': 'success',
        'message': 'Laporan telah ditolak (dihapus).',
        'action': 'rejected'
    })

@csrf_exempt
@user_passes_test(is_admin, login_url='/login')
def admin_accept_report(request, id):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid method.'}, status=405)
    
    try:
        report = get_object_or_404(Report, id=id)
        user_to_strike = report.reported_user
        
        user_to_strike.strikes += 1
        user_to_strike.save() 
        
        report_message = f"Laporan terhadap {user_to_strike.username} diterima. Strike sekarang: {user_to_strike.strikes}."
        
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

@csrf_exempt
@login_required(login_url='/login')
def request_writer_role(request):
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
    if request.user.role != 'reader':
        msg = 'Only readers can request to become writers.'
        if is_ajax:
            return JsonResponse({'status': 'error', 'message': msg}, status=403)
        else:
            messages.error(request, msg)
            return redirect('users:show_profile', id=request.user.id)
    existing_request = WriterRequest.objects.filter(user=request.user, status='pending').first()

    if request.method == 'POST':
        if not is_ajax:
            return JsonResponse({'status': 'error', 'message': 'Invalid request.'}, status=400)
        
        if existing_request:
            return JsonResponse({'status': 'error', 'message': 'You already have a pending request.'}, status=400)

        form = WriterRequestForm(request.POST)
        if form.is_valid():
            req = form.save(commit=False)
            req.user = request.user

            req.save()
            return JsonResponse({
                'status': 'success',
                'message': 'Your request has been submitted. Admin will review it.'
            })
        else:
            errors = form.errors.as_json()
            return JsonResponse({'status': 'error', 'errors': errors}, status=400)
    form = WriterRequestForm()
    context = {
        'form': form,
        'existing_request': existing_request
    }
    return render(request, 'request_writer_role.html', context)

@csrf_exempt
@user_passes_test(is_admin, login_url='/login')
def admin_approve_writer(request, id):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid method.'}, status=405)
    
    try:
        writer_req = get_object_or_404(WriterRequest, id=id)
        user_to_promote = writer_req.user
        
        user_to_promote.role = 'writer'
        user_to_promote.save()
        
        writer_req.status = 'approved'
        writer_req.save()
        
        WriterRequest.objects.filter(user=user_to_promote, status='pending').delete()
        
        return JsonResponse({
            'status': 'success',
            'message': f"{user_to_promote.username} has been promoted to Writer.",
            'action': 'approved',
            'user_id': user_to_promote.id,
            'new_role': user_to_promote.role
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@csrf_exempt
@user_passes_test(is_admin, login_url='/login')
def admin_reject_writer(request, id):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid method.'}, status=405)
        
    try:
        writer_req = get_object_or_404(WriterRequest, id=id)

        writer_req.status = 'rejected'
        writer_req.save()
        
        return JsonResponse({
            'status': 'success',
            'message': 'The request has been rejected.',
            'action': 'rejected'
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@login_required
def show_current_user_profile(request):
    user = request.user
    
    if user.profile_picture:
        pic_url = user.profile_picture.url
    else:
        pic_url = static('image/default_profile_picture.jpg')

    return JsonResponse({
        'status': 'success',
        'data': {
            'id': user.id,
            'username': user.username,
            'full_name': f"{user.first_name or ''} {user.last_name or ''}".strip(),
            'bio': user.bio or "-",
            'role': user.role,
            'strikes': user.strikes,
            'date_joined': user.date_joined.strftime('%Y-%m-%d'),
            'profile_picture_url': pic_url,
        }
    })