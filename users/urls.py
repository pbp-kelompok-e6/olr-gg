from django.urls import path
from .views import edit_profile, report_user, show_profile, load_news, change_profile_pic

app_name = 'users'

urlpatterns = [
    path('edit_profile/', edit_profile, name='edit_profile'),
    path('show_profile/<int:id>/', show_profile, name='show_profile'),
    path('load_news/<int:id>/', load_news, name='load_news'),
    path('change_pic', change_profile_pic, name='change_pic'),
    path('report_user/<int:id>/', report_user, name='report_user'),
]