# readinglist/urls.py
from django.urls import path
from . import views

app_name = 'readinglist'

urlpatterns = [
    path('', views.show_reading_lists, name='show_lists'), 
    path('create_or_rename/', views.create_or_rename_list_ajax, name='create_list'), # Create
    path('create_or_rename/<uuid:list_id>/', views.create_or_rename_list_ajax, name='rename_list'), # Rename
    path('delete/<uuid:list_id>/', views.delete_list_ajax, name='delete_list'), # Delete
    path('add_remove/<uuid:news_id>/', views.add_to_list_ajax, name='add_remove_news'), 
    path('toggle_read/<int:item_id>/', views.toggle_read_status_ajax, name='toggle_read'), 
    path('api/lists/', views.get_user_lists_ajax, name='get_user_lists'), 
    path('api/status/<uuid:news_id>/', views.get_news_list_status_ajax, name='get_news_list_status'), 
    path('lists/create/', views.create_list, name='create_list'),
    path('lists/<uuid:list_id>/rename/', views.rename_list, name='rename_list'),
    path('lists/<uuid:list_id>/delete/', views.delete_list, name='delete_list'),
    path('items/<int:item_id>/toggle-read/', views.toggle_read, name='toggle_read'),
]