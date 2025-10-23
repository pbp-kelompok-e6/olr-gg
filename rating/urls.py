from django.urls import path
from . import views

app_name = 'rating'

urlpatterns = [
    path('add/<int:berita_id>/', views.add_rating, name='add_review'),
    path('delete/<int:rating_id>/', views.delete_rating, name='delete_rating'),
]