from django.shortcuts import render

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from berita.models import News
from .models import Rating
from .forms import ReviewForm
from django.http import HttpResponseForbidden

@login_required
def add_rating(request, news_id):
    news = get_object_or_404(News, id=news_id)
    
    # Cek apakah user sudah pernah mereview news ini sebelumnya
    existing_review = Rating.objects.filter(news=news, user=request.user).first()
    if existing_review:
        messages.error(request, "Anda sudah memberikan review untuk news ini")
        return redirect('detail_news', news_id=news_id)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.news = news
            review.user = request.user
            review.save()
            messages.success(request, "Review berhasil ditambahkan")
            return redirect('detail_news', news_id=news_id)
    else:
        form = ReviewForm()

    context = {
        'form': form,
        'news': news
    }
    return render(request, 'rating/add_review.html', context)

@login_required
def delete_rating(request, rating_id):
    # Get the rating object or return 404 if not found
    rating = get_object_or_404(Rating, id=rating_id)
    
    # Cek apakah user pemilik rating ini
    if rating.user != request.user:
        return HttpResponseForbidden("Kamu tidak memiliki izin untuk menghapus rating ini.")
    
    # Simpan id berita sebelum dihapus
    news_id = rating.news.id

    rating.delete()
    
    messages.success(request, "Rating berhasil dihapus.")
    return redirect('news_detail', news_id=news_id)

@login_required
def edit_rating(request, rating_id):
    rating = get_object_or_404(Rating, id=rating_id)
    
    # Cek apakah user memiliki rating ini
    if rating.user != request.user:
        return HttpResponseForbidden("Kamu tidak memiliki izin untuk mengedit rating ini.")

    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=rating)
        if form.is_valid():
            form.save()
            messages.success(request, "Rating berhasil diperbarui.")
            return redirect('detail_news', news_id=rating.news.id)
    else:
        form = ReviewForm(instance=rating)

    context = {
        'form': form,
        'news': rating.news,
        'rating': rating
    }
    return render(request, 'rating/edit_rating.html', context)