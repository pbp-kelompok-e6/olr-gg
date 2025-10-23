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

@login_required(login_url='/login')
def show_comments(request, id):
    comment= get_object_or_404(Comments, pk=id)

    context = {
        'comment': comment,
        'news': comment.news,
        'comment_user': comment.user
    }

    return render(request, "comments_detail.html", context)


@login_required(login_url='/login')
@csrf_exempt
@require_POST
def add_comment(request):
    content = strip_tags(request.POST.get("content")) # strip HTML tags!
    user = request.user
    news = get_object_or_404(News, pk=request.POST.get("news_id"))
    

    comment_baru = Comments( 
        content=content,
        user=user,
        news=news
    )
    comment_baru.save()

    return JsonResponse({"status": "SUCCESS", "message": "Comment created successfully."}, status=201)

@csrf_exempt
@require_POST
@login_required
def edit_comment(request, id):
    comment = get_object_or_404(Comments, pk=id, user=request.user)  # pastikan hanya user sendiri
    comment.content = strip_tags(request.POST.get("content"))
    comment.save()

    return JsonResponse({"status": "SUCCESS", "message": "Comment updated successfully."}, status=200)

@login_required(login_url='/login')
@csrf_exempt
@require_POST
def delete_comment(request, id):
    try:
        comment = Comments.objects.get(pk=id)
        if comment.user != request.user and not request.user.is_staff:
            return JsonResponse({"status": "ERROR", "message": "Access denied."}, status=403)
        comment.delete()
        return JsonResponse({"status": "SUCCESS", "message": "Comment deleted successfully."}, status=200)
    except Comments.DoesNotExist:
        return JsonResponse({"status": "ERROR", "message": "Comment not found or access denied."}, status=404)