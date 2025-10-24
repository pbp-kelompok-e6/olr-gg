from django.urls import path
from . import views

app_name = 'rating'

urlpatterns = [
    path('get/<uuid:news_id>/', views.get_ratings_json, name='get_ratings'),
    path('add/<uuid:news_id>/', views.add_rating, name='add_rating'),
    path('edit/<int:rating_id>/', views.edit_rating, name='edit_rating'),
    path('delete/<int:rating_id>/', views.delete_rating, name='delete_rating'),
]