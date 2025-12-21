from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
User = get_user_model()

@csrf_exempt
def login(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
        except json.JSONDecodeError:
            username = request.POST.get('username')
            password = request.POST.get('password')

        if username:
            try:
                user_check = User.objects.get(username=username)
                
                if not user_check.is_active:
                    return JsonResponse({
                        "status": False,
                        "message": "Akun anda telah diblokir karena telah mencapai 3 strike. Silakan hubungi admin."
                    }, status=403) 
            
            except User.DoesNotExist:
                pass

        user = authenticate(username=username, password=password)

        if user is not None:
            auth_login(request, user)
            
            return JsonResponse({
                "username": user.username,
                "status": True,
                "message": "Login successful!",
                "role": getattr(user, 'role', 'user') 
            }, status=200)
        else:
            return JsonResponse({
                "status": False,
                "message": "Login failed, please check your username or password."
            }, status=401)

    return JsonResponse({"status": False, "message": "Invalid method"}, status=405)
    
@csrf_exempt
def register(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data['username']
        password1 = data['password1']
        password2 = data['password2']
        firstname = data['first_name']
        lastname = data['last_name']

        # Check if the passwords match
        if password1 != password2:
            return JsonResponse({
                "status": False,
                "message": "Passwords do not match."
            }, status=400)
        
        # Check if the username is already taken
        if User.objects.filter(username=username).exists():
            return JsonResponse({
                "status": False,
                "message": "Username already exists."
            }, status=400)
        
        # Create the new user
        user = User.objects.create_user(username=username, password=password1, role = "reader", first_name = firstname, last_name = lastname)
        user.save()
        
        return JsonResponse({
            "username": user.username,
            "status": 'success',
            "message": "User created successfully!"
        }, status=200)
    
    else:
        return JsonResponse({
            "status": False,
            "message": "Invalid request method."
        }, status=400)
    
@csrf_exempt
def logout(request):
    username = request.user.username
    try:
        auth_logout(request)
        return JsonResponse({
            "username": username,
            "status": True,
            "message": "Logged out successfully!"
        }, status=200)
    except:
        return JsonResponse({
            "status": False,
            "message": "Logout failed."
        }, status=401)