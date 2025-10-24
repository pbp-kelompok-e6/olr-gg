# readinglist/urls.py
from django.urls import path
from .views import (
    show_reading_lists, 
    add_to_list_ajax, 
    create_or_rename_list_ajax, 
    delete_list_ajax,
    toggle_read_status_ajax,
    get_user_lists_ajax,
    get_user_lists_ajax,
    get_news_list_status_ajax
)

app_name = 'readinglist'

urlpatterns = [
    path('', show_reading_lists, name='show_lists'), 
    path('create_or_rename/', create_or_rename_list_ajax, name='create_list'), # Create
    path('create_or_rename/<uuid:list_id>/', create_or_rename_list_ajax, name='rename_list'), # Rename
    path('delete/<uuid:list_id>/', delete_list_ajax, name='delete_list'), # Delete
    path('add_remove/<uuid:news_id>/', add_to_list_ajax, name='add_remove_news'), 
    path('toggle_read/<int:item_id>/', toggle_read_status_ajax, name='toggle_read'), 
    path('api/lists/', get_user_lists_ajax, name='get_user_lists'), 
    path('api/status/<uuid:news_id>/', get_news_list_status_ajax, name='get_news_list_status'), 
]