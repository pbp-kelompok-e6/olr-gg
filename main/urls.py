from django.urls import path, include
from main.views import show_main, register, login_user, logout_user
from users import views as user_views

app_name = 'main'

urlpatterns = [
    path('', show_main, name='show_main'),
    path('register/', register, name='register'),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),
    path('edit_profile/', user_views.edit_profile, name='edit_profile'),
    path('readinglist/', include(('readinglist.urls', 'readinglist'))),
]
