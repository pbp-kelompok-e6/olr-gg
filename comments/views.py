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
from django.views.decorators.http import require_POST
from django.utils.html import strip_tags


def get_comment_data(comment):
    """Helper function to format comment data for JSON response"""
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
            
            # Use news_id from URL parameter instead of POST
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


@require_POST
@login_required()
def edit_comment(request, id, news_id):
    try:
        comment = get_object_or_404(Comments, pk=id)
        
        # Check permissions
        if comment.user != request.user and not request.user.is_staff:
            return JsonResponse({
                "status": "ERROR",
                "message": "Access denied."
            }, status=403)
        
        content = strip_tags(request.POST.get("content"))
        
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

@require_POST
def delete_comment(request, id, news_id):
    try:
        comment = Comments.objects.get(pk=id)
        
        # Check permissions
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
        }
        for comment in comment_list
    ]

    return JsonResponse(data, safe=False)