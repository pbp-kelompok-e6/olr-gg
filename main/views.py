from django.shortcuts import render, redirect, get_object_or_404
from berita.models import News
from django.http import HttpResponse, HttpResponseNotFound
from django.core import serializers
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from users.forms import CustomUserCreationForm as UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
import datetime
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.html import strip_tags
import json
# Create your views here.

def show_main(request):
    filter_type = request.GET.get("filter", "all")  # default 'all'
    if filter_type == "all":
        news_list = News.objects.all()
    else:
        news_list = News.objects.filter(user=request.user)
    context = {
        'news_list': news_list,
    }
    return render(request, "main.html", context)

def register(request):
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json'
    if request.method == "POST":
        if is_ajax:
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                return JsonResponse({"status": "ERROR", "message": "Invalid JSON format."}, status=400)
            form = UserCreationForm(data)
        else:
            form = UserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()
            messages.success(request, 'Your account has been successfully created!')
            if is_ajax:
                return JsonResponse({"status": "SUCCESS", "message": "Account created successfully."}, status=201)
            return redirect('main:login')

        # form invalid
        if is_ajax:
            errors = dict(form.errors.items())
            return JsonResponse({"status": "ERROR", "message": "Failed to create account. Please check your input.", "errors": errors}, status=400)

    # GET or fallback
    form = UserCreationForm()
    context = {'form': form}
    return render(request, 'register.html', context)

def login_user(request):
   if request.method == 'POST':
      is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'

      if is_ajax:
         try:
            data = json.loads(request.body)
         except json.JSONDecodeError:
            return JsonResponse({"status": "ERROR", "message": "Invalid JSON format."}, status=400)
      else:
         data = request.POST

      form = AuthenticationForm(request, data=data)

      if form.is_valid():
         user = form.get_user()
         login(request, user)

         if is_ajax:
            response = JsonResponse({"status": "SUCCESS", "message": "Login successful!"}, status=200)
            response.set_cookie('last_login', str(datetime.datetime.now()))
            return response

         response = HttpResponseRedirect(reverse("main:show_main"))
         response.set_cookie('last_login', str(datetime.datetime.now()))
         return response

      # form invalid
      if is_ajax:
         errors = dict(form.errors.items())
         return JsonResponse({"status": "ERROR", "message": "Invalid credentials or missing input.", "errors": errors}, status=400)

   # GET or fallback
   form = AuthenticationForm(request)
   context = {'form': form}
   return render(request, 'login.html', context)

def logout_user(request):
    logout(request)
    response = HttpResponseRedirect(reverse('main:login'))
    response.delete_cookie('last_login')
    return response




