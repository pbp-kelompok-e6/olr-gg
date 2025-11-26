# forum/views.py
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import ForumPost, ForumComment
from django.urls import reverse
import json
from django.utils.html import strip_tags
from .forms import ForumPostForm
from django.template.defaultfilters import date as _date

def forum_view(request):
    all_posts = ForumPost.objects.all().order_by('-created_at')
    context = {
        'posts': all_posts,
    }
    return render(request, 'forum.html', context)

@login_required
def create_post_ajax(request):
    if request.method == 'POST':
        try:
            # Validasi parsing JSON
            data = json.loads(request.body)
            form = ForumPostForm(data)

            if form.is_valid():
                post = form.save(commit=False)
                post.author = request.user
                post.save()

                return JsonResponse({
                    'status': 'success',
                    'post': {
                        'id': post.id,
                        'title': post.title,
                        'author_username': post.author.username,
                        'url': reverse('forum:post_detail_view', kwargs={'post_id': post.id}),
                        'category_code': post.category,
                        'category_display': post.get_category_display(),
                        'created_at_formatted': _date(post.created_at, "M d, Y"),
                        'comment_count': 0 
                    }
                })
            else:
                return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
        
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON format'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)


@login_required
def edit_post_ajax(request, post_id):
    # Kita letakkan get_object di luar try karena Django sudah handle 404 scara otomatis
    post = get_object_or_404(ForumPost, id=post_id, author=request.user)
    
    if request.method == 'PATCH': 
        try:
            data = json.loads(request.body)
            
            # Update field hanya jika data dikirimkan
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
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON format'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method. Use PATCH.'}, status=405)


@login_required
def delete_post_ajax(request, post_id):
    post = get_object_or_404(ForumPost, id=post_id, author=request.user)
    
    if request.method == 'DELETE':
        try:
            post.delete()
            return JsonResponse({'status': 'success', 'redirect_url': reverse('forum:forum_view')})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
            
    return JsonResponse({'status': 'error', 'message': 'Invalid request method. Use DELETE.'}, status=405)

def post_detail_view(request, post_id):
    post = get_object_or_404(ForumPost, id=post_id)
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
        try:
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
                    'author_username': comment.author.username,
                    'author_role': comment.author.role,
                    'created_at': comment.created_at.isoformat(), 
                    'updated_at': comment.updated_at.isoformat(),
                }
            })
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON format'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

@login_required
def delete_comment_ajax(request, comment_id):
    comment = get_object_or_404(ForumComment, id=comment_id, author=request.user)
    
    if request.method == 'DELETE':
        try:
            comment.delete()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method. Use DELETE.'}, status=405)


@login_required
def edit_comment_ajax(request, comment_id):
    comment = get_object_or_404(ForumComment, id=comment_id, author=request.user)
    
    if request.method == 'PATCH':
        try:
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
                    'updated_at': comment.updated_at.isoformat(),
                }
            })
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON format'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method. Use PATCH.'}, status=405)

@login_required
def get_post_data_ajax(request, post_id):
    post = get_object_or_404(ForumPost, id=post_id, author=request.user)
    if request.method == 'GET':
        return JsonResponse({
            'status': 'success',
            'post': {
                'id': post.id,
                'title': post.title,
                'content': post.content,
                'category': post.category,
            }
        })
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)