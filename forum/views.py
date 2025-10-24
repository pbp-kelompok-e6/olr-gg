# forum/views.py
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import ForumPost, ForumComment
from django.urls import reverse
import json
from django.utils.html import strip_tags
from .forms import ForumPostForm

def forum_view(request):
    """
    Merender halaman forum utama dengan daftar semua post.
    """
    all_posts = ForumPost.objects.all().order_by('-created_at')
    context = {
        'posts': all_posts,
    }
    return render(request, 'forum.html', context)


@login_required
def create_post_ajax(request):
    """
    Membuat post baru menggunakan AJAX dengan validasi dari Django Forms.
    """
    if request.method == 'POST':
        data = json.loads(request.body)
        # Django Forms akan menangani sanitasi dasar untuk keamanan
        form = ForumPostForm(data)

        if form.is_valid():
            # jika form valid, buat objek post tanpa menyimpannya dulu ke DB
            post = form.save(commit=False)
            post.author = request.user  # Tetapkan author post
            post.save()                 # Simpan post ke database

            return JsonResponse({
                'status': 'success',
                'post': {
                    'id': post.id,
                    'title': post.title,
                    'content': post.content,
                    'author': post.author.username,
                    'url': reverse('forum:post_detail_view', kwargs={'post_id': post.id}),
                    'category_code': post.category,
                    'category_display': post.get_category_display()
                }
            })
        else:
            # kirim pesan error yang dihasilkan oleh form jika tidak valid
            return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)


@login_required
def edit_post_ajax(request, post_id):
    """
    Mengedit post yang ada menggunakan AJAX dan membersihkan input dengan strip_tags.
    """
    post = get_object_or_404(ForumPost, id=post_id, author=request.user)
    if request.method == 'POST':
        data = json.loads(request.body)
        post.title = strip_tags(data.get('title', post.title))
        post.content = strip_tags(data.get('content', post.content))
        post.category = data.get('category', post.category)
        post.save()
        
        return JsonResponse({
            'status': 'success',
            'post': {
                'title': post.title,
                'content': post.content,
                'category_display': post.get_category_display()
            }
        })
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)


@login_required
def delete_post_ajax(request, post_id):
    """
    Menghapus post menggunakan AJAX.
    """
    post = get_object_or_404(ForumPost, id=post_id, author=request.user)
    if request.method == 'POST':
        post.delete()
        return JsonResponse({'status': 'success', 'redirect_url': reverse('forum:forum_view')})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

def post_detail_view(request, post_id):
    """
    Menampilkan halaman detail untuk satu post beserta komentarnya.
    """
    post = get_object_or_404(ForumPost, id=post_id)
    comments = post.comments.all().order_by('created_at')
    context = {
        'post': post,
        'comments': comments,
    }
    return render(request, 'post_detail.html', context)


@login_required
def create_comment_ajax(request, post_id):
    """
    Membuat komentar baru pada sebuah post menggunakan AJAX.
    """
    post = get_object_or_404(ForumPost, id=post_id)
    if request.method == 'POST':
        data = json.loads(request.body)
        content = strip_tags(data.get('content'))

        if not content:
            return JsonResponse({'status': 'error', 'message': 'Comment cannot be empty.'}, status=400)

        comment = ForumComment.objects.create(post=post, author=request.user, content=content)
        
        return JsonResponse({
            'status': 'success',
            'comment': {
                'id': comment.id,
                'content': comment.content,
                'author': comment.author.username,
            }
        })
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)


@login_required
def delete_comment_ajax(request, comment_id):
    """
    Menghapus komentar menggunakan AJAX.
    """
    comment = get_object_or_404(ForumComment, id=comment_id, author=request.user)
    if request.method == 'POST':
        comment.delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)


@login_required
def edit_comment_ajax(request, comment_id):
    """
    Mengedit komentar yang ada menggunakan AJAX.
    """
    comment = get_object_or_404(ForumComment, id=comment_id, author=request.user)
    if request.method == 'POST':
        data = json.loads(request.body)
        new_content = strip_tags(data.get('content'))
        
        if not new_content:
            return JsonResponse({'status': 'error', 'message': 'Comment cannot be empty.'}, status=400)
            
        comment.content = new_content
        comment.save()
        
        return JsonResponse({
            'status': 'success',
            'comment': {
                'id': comment.id,
                'content': comment.content,
            }
        })
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)