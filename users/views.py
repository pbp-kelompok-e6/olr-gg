
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import CustomUserChangeForm # Impor form baru

@login_required(login_url='/login') # Pastikan user sudah login
def edit_profile(request):
    if request.method == 'POST':
        # 1. Saat user submit, isi form dengan data POST
        # 2. WAJIB: sertakan request.FILES untuk file (gambar)
        # 3. WAJIB: sertakan 'instance=request.user' agar Django tahu
        #    user mana yang sedang di-UPDATE, bukan membuat baru.
        form = CustomUserChangeForm(request.POST, request.FILES, instance=request.user)
        
        if form.is_valid():
            form.save()
            messages.success(request, 'Profil kamu berhasil diperbarui!')
            return redirect('nama_url_edit_profil') 
    
    else:
        form = CustomUserChangeForm(instance=request.user)

    context = {
        'form': form
    }
    return render(request, 'edit_profile.html', context)