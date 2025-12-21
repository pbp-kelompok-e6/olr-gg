from django.urls import path
from main.views import show_main, register, login_user, logout_user
from users import views as user_views
from comments.views import get_comments_json,show_comments, edit_comment, delete_comment, add_comment,api_create_comments,api_edit_comments,api_delete_comments

app_name = 'comments'

urlpatterns = [
    path('add_comment/', add_comment, name='create_comment'),
    path('<uuid:comment_id>/edit/', edit_comment, name='edit_comment'),
    path('<uuid:comment_id>/delete/', delete_comment, name='delete_comment'),
    path('add_comment_flutter/', api_create_comments, name='create_comment_flutter'),
    path('<uuid:comment_id>/edit_flutter/', api_edit_comments, name='edit_comment_flutter'),
    path('<uuid:comment_id>/delete_flutter/', api_delete_comments, name='delete_comment_flutter'),
    path('<uuid:news_id>/json/', get_comments_json, name='get_comments_json'),
]