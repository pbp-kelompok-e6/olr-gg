from django.urls import path
from main.views import show_main, register, login_user, logout_user
from users import views as user_views
from comments.views import show_comments, edit_comment, delete_comment, add_comment

app_name = 'main'

urlpatterns = [
    path('add_comment/', add_comment, name='create_comment'),
    path('<uuid:comment_id>/edit/', edit_comment, name='edit_comment'),
    path('<uuid:comment_id>/delete/', delete_comment, name='delete_comment'),
]