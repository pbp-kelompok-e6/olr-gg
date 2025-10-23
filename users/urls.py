from django.urls import path
from .views import edit_profile, show_profile

app_name = 'users'

urlpatterns = [
    path('edit_profile/', edit_profile, name='edit_profile'),
    path('show_profile/<int:id>/', show_profile, name='show_profile'),
]