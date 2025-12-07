from django.utils import timezone
from django.shortcuts import render

# Create your views here.
from django.http import HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from berita.forms import newsForm
from berita.models import News
from comments.models import Comments
from main.views import login_required
from django.http import JsonResponse, HttpResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_http_methods
from django.utils.html import strip_tags
import json


def get_comment_data(comment):
    return {
        "id": str(comment.id),
        "content": comment.content,
        "user": comment.user.username,
        "profile_picture": comment.user.profile_picture.url if comment.user.profile_picture else None,
        "role": comment.user.role if hasattr(comment.user, 'role') else None,
        "created_at": comment.created_at.strftime('%B %d, %Y %H:%M') if comment.created_at else None,
        "updated_at": comment.updated_at.strftime('%B %d, %Y %H:%M') if comment.updated_at else None,
    }


def show_comments(request, id):
    comment= get_object_or_404(Comments, pk=id)

    context = {
        'comment': comment,
        'news': comment.news,
        'comment_user': comment.user
    }

    return render(request, "comments_detail.html", context)


@login_required()
@require_POST
def add_comment(request, news_id):
    try:
        content = strip_tags(request.POST.get("content"))
        user = request.user
        if user.is_authenticated:
            if not content:
                return JsonResponse({
                    "status": "ERROR", 
                    "message": "Content is required."
                }, status=400)
            
            news = get_object_or_404(News, pk=news_id)
            
            comment_baru = Comments(
                content=content,
                user=user,
                news=news
            )
            comment_baru.save()

            return JsonResponse({
                "status": "SUCCESS", 
                "message": "Comment created successfully.",
                "comment": get_comment_data(comment_baru)
            }, status=201)
        else:
            return JsonResponse({
                "status": "ERROR", 
                "message": "Login required."
            }, status=401)
    except Exception as e:
        return JsonResponse({
            "status": "ERROR", 
            "message": str(e)
        }, status=500)


@login_required()
@require_http_methods(["PUT"])
def edit_comment(request, id, news_id):
    try:
        comment = get_object_or_404(Comments, pk=id)
        

        if comment.user != request.user and not request.user.is_staff:
            return JsonResponse({
                "status": "ERROR",
                "message": "Access denied."
            }, status=403)
        
        # Parse JSON body for PUT request
        try:
            data = json.loads(request.body.decode('utf-8'))
            content = strip_tags(data.get("content", ""))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return JsonResponse({
                "status": "ERROR",
                "message": "Invalid JSON data."
            }, status=400)
        
        if not content:
            return JsonResponse({
                "status": "ERROR",
                "message": "Content is required."
            }, status=400)
        
        comment.content = content
        comment.updated_at = timezone.now()
        comment.save()

        return JsonResponse({
            "status": "SUCCESS",
            "message": "Comment updated successfully.",
            "comment": get_comment_data(comment)
        }, status=200)
    except Comments.DoesNotExist:
        return JsonResponse({
            "status": "ERROR",
            "message": "Comment not found."
        }, status=404)
    except Exception as e:
        return JsonResponse({
            "status": "ERROR",
            "message": str(e)
        }, status=500)

@login_required()
@require_http_methods(["DELETE"])
def delete_comment(request, id, news_id):
    try:
        comment = Comments.objects.get(pk=id)
        
        if comment.user != request.user and not request.user.is_staff:
            return JsonResponse({
                "status": "ERROR",
                "message": "Access denied."
            }, status=403)
        
        comment.delete()
        
        return JsonResponse({
            "status": "SUCCESS",
            "message": "Comment deleted successfully."
        }, status=200)
    except Comments.DoesNotExist:
        return JsonResponse({
            "status": "ERROR",
            "message": "Comment not found."
        }, status=404)
    except Exception as e:
        return JsonResponse({
            "status": "ERROR",
            "message": str(e)
        }, status=500)

def show_comments_json(request):
    comment_list = Comments.objects.all()
    data = [
        {
            'id': comment.id,
            'news_id': comment.news.id,
            'user_id': comment.user_id,
            'content': comment.content,
            'created_at': comment.created_at.isoformat() if comment.created_at else None,
            'updated_at': comment.updated_at.isoformat() if comment.updated_at else None,
            'user_username': comment.user.username if comment.user_id else None,
            'user_role': comment.user.role if comment.user_id and hasattr(comment.user, 'role') else None,
        }
        for comment in comment_list
    ]

    return JsonResponse(data, safe=False)

def get_comments_json(request, news_id):
    comment_list = Comments.objects.filter(news__id=news_id)
    data = [
        {
            'id': comment.id,
            'news_id': comment.news.id,
            'user_id': comment.user_id,
            'content': comment.content,
            'created_at': comment.created_at.isoformat() if comment.created_at else None,
            'updated_at': comment.updated_at.isoformat() if comment.updated_at else None,
            'user_username': comment.user.username if comment.user_id else None,
            'user_role': comment.user.role if comment.user_id and hasattr(comment.user, 'role') else None,
        }
        for comment in comment_list
    ]

    return JsonResponse(data, safe=False)

@csrf_exempt
def api_create_comments(request):
    if request.method == 'POST':
        try:

            if not request.user.is_authenticated:
                return JsonResponse({"status": "error", "message": "Authentication required"}, status=401)
            

            news_id = request.POST.get('news_id')
            content = request.POST.get('content')
            
            content = strip_tags(content) if content else ''
            
            if not content or not content.strip():
                return JsonResponse({"status": "error", "message": "Content is required"}, status=400)
            
            if not news_id:
                return JsonResponse({"status": "error", "message": "News ID is required"}, status=400)
            
            news = get_object_or_404(News, pk=news_id)
            comment = Comments.objects.create(
                news=news,
                user=request.user,
                content=content
            )
            
            return JsonResponse({
                "status": "success",
                "message": "Comment created successfully",
                "comment": get_comment_data(comment)
            }, status=201)
        except Exception as e:
            import traceback
            print(f"ERROR: {str(e)}")
            print(traceback.format_exc())
            return JsonResponse({"status": "error", "message": str(e)}, status=400)
    
    return JsonResponse({"error": "Invalid request"}, status=400)
    

    
@csrf_exempt
@login_required
def api_edit_news(request, comment_id):
    if request.method == 'POST':
        try:
            comment = Comments.objects.get(pk=comment_id)
            data = json.loads(request.body)
            user = comment.user;
            comment.content = strip_tags(data.get("content", comment.content))
            comment.updated_at = timezone.now()
            comment.save()
            return JsonResponse({"status": "success"}, status=200)
        except Comments.DoesNotExist:
            return JsonResponse({"error": "Comment not found"}, status=404)
    return JsonResponse({"error": "Invalid request"}, status=400)
    
@csrf_exempt
@login_required
def api_delete_news(request, comment_id):
    if request.method == 'POST':
        try:
            comment = Comments.objects.get(pk=comment_id)
            comment.delete()
            return JsonResponse({"status": "success"}, status=200)
        except Comments.DoesNotExist:
            return JsonResponse({"error": "Comment not found"}, status=404)
    return JsonResponse({"error": "Invalid request"}, status=400)
    