from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from .models import ForumPost, ForumComment
from django.core.paginator import Paginator
from django.forms.models import model_to_dict
from django.urls import reverse
import json

POSTS_PER_PAGE = 10 # Jumlah post yang akan di-load setiap kali

@login_required
def forum_view(request):
    """
    Renders the main forum page with a list of all posts.
    """
    all_posts = ForumPost.objects.all().order_by('-created_at')
    context = {
        'posts': all_posts,
    }
    return render(request, 'forum.html', context)

@login_required
def create_post_ajax(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        title = data.get('title')
        content = data.get('content')

        if not title or not content:
            return JsonResponse({'status': 'error', 'message': 'Title and content cannot be empty.'}, status=400)

        post = ForumPost.objects.create(author=request.user, title=title, content=content)
        
        # The fix is here: we now generate the URL and add it to the response
        return JsonResponse({
            'status': 'success',
            'post': {
                'id': post.id,
                'title': post.title,
                'author': post.author.username,
                'url': reverse('forum:post_detail_view', kwargs={'post_id': post.id}) # <-- THIS IS THE NEW LINE
            }
        })
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

@login_required
def edit_post_ajax(request, post_id):
    post = get_object_or_404(ForumPost, id=post_id, author=request.user)
    if request.method == 'POST':
        data = json.loads(request.body)
        post.title = data.get('title', post.title)
        post.content = data.get('content', post.content)
        post.save()
        return JsonResponse({
            'status': 'success',
            'post': {
                'title': post.title,
                'content': post.content,
            }
        })
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

@login_required
def delete_post_ajax(request, post_id):
    post = get_object_or_404(ForumPost, id=post_id, author=request.user)
    if request.method == 'POST':
        post.delete()
        return JsonResponse({'status': 'success', 'redirect_url': reverse('forum:forum_view')})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

@login_required
def post_detail_view(request, post_id):
    """
    Renders the detail page for a single post, including its comments.
    """
    post = get_object_or_404(ForumPost, id=post_id)
    # Get all comments related to this post
    comments = post.comments.all().order_by('created_at')
    context = {
        'post': post,
        'comments': comments,
    }
    return render(request, 'post_detail.html', context)

@login_required
def create_comment_ajax(request, post_id):
    post = get_object_or_404(ForumPost, id=post_id)
    if request.method == 'POST':
        data = json.loads(request.body)
        content = data.get('content')

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
    comment = get_object_or_404(ForumComment, id=comment_id, author=request.user)
    if request.method == 'POST':
        comment.delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

@login_required
def edit_comment_ajax(request, comment_id):
    comment = get_object_or_404(ForumComment, id=comment_id, author=request.user)
    if request.method == 'POST':
        data = json.loads(request.body)
        new_content = data.get('content')
        
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

# COMMENTS_PER_PAGE = 10 # Jumlah komentar yang akan di-load setiap kali

# def load_more_comments_ajax(request, post_id):
#     """
#     Mengambil data komentar tambahan untuk sebuah post secara spesifik.
#     """
#     # 1. Dapatkan post yang komentarnya ingin kita muat
#     post = get_object_or_404(ForumPost, id=post_id)
    
#     # 2. Ambil 'offset' dari parameter URL (?offset=...) untuk pagination
#     # Ini memberitahu kita berapa banyak komentar yang harus dilewati (karena sudah ditampilkan)
#     offset = int(request.GET.get('offset', 0))
#     limit = COMMENTS_PER_PAGE
    
#     # 3. Query komentar untuk post tersebut, diurutkan dari yang paling lama
#     comments_query = post.comments.all().order_by('created_at')[offset:offset+limit]
    
#     # 4. Ubah hasil query menjadi format JSON yang bisa dibaca oleh JavaScript
#     comments_data = [{
#         'id': comment.id,
#         'content': comment.content,
#         'author': comment.author.username,
#         'is_author': request.user == comment.author, # Penting untuk menampilkan tombol edit/delete di frontend
#         'created_at': comment.created_at.strftime('%d %b %Y, %H:%M')
#     } for comment in comments_query]

#     # 5. Cek apakah masih ada komentar lain setelah batch ini
#     has_more = post.comments.count() > offset + limit
    
#     # 6. Kirim respons kembali ke browser
#     return JsonResponse({
#         'status': 'success',
#         'comments': comments_data,
#         'has_more': has_more
#     })