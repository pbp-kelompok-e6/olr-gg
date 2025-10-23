from django.urls import path
from main.views import show_main, register, login_user, logout_user
from berita.views import show_news, create_news, edit_news, delete_news, show_json, show_json_by_id

app_name = 'main'

urlpatterns = [
    path('', show_main, name='show_main'),
    path('register/', register, name='register'),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),
    path('news/<str:id>/', show_news, name='show_news'),
    path('news/<uuid:id>/edit/', edit_news, name='edit_news'),
    path('news/<uuid:id>/delete/', delete_news, name='delete_news'),
    path('create-news/', create_news, name='create_news'),
    path('json/', show_json, name='show_json'),
    path('json/<str:news_id>/', show_json_by_id, name='show_json_by_id'),
]