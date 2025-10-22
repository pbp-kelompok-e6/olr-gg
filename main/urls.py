from django.urls import path
from main.views import show_main, register, login_user, logout_user
from berita.views import show_berita, add_berita, edit_berita, delete_berita
from users import views as user_views

app_name = 'main'

urlpatterns = [
    path('', show_main, name='show_main'),
    path('register/', register, name='register'),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),
    path('edit_profile/', user_views.edit_profile, name='edit_profile'),
    path('berita/<str:id>/', show_berita, name='show_berita'),
    path('berita/<uuid:id>/edit', edit_berita, name='edit_berita'),
    path('berita/<uuid:id>/delete', delete_berita, name='delete_berita'),
    path('create-berita-ajax', add_berita, name='add_berita'),
]