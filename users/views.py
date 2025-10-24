from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import CustomUserChangeForm, ProfilePictureForm, ReportUserForm
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

            usertarget.strikes += 1
            usertarget.save() 

            return JsonResponse({
                'status': 'success',
                'message': f'User {usertarget.username} berhasil dilaporkan. Strike ditambahkan.'
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