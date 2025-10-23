from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import CustomUserChangeForm 
from django.shortcuts import get_object_or_404
from .models import CustomUser as User
from django.contrib.auth import get_user_model

User = get_user_model()

@login_required(login_url='/login')
def edit_profile(request):
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, request.FILES, instance=request.user)
        
        if form.is_valid():
            form.save()
            return JsonResponse({'status': 'success', 'message': 'Profile berhasil di update.'})
    
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
