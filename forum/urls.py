from django.urls import path
from forum import views

app_name = 'forum'

urlpatterns = [
    # Halaman utama forum
    path('', views.forum_view, name='forum_view'),

    path('post/<int:post_id>/', views.post_detail_view, name='post_detail_view'),

    # For Posts (Create is on main page, Edit/Delete are on detail page)
    path('ajax/create-post/', views.create_post_ajax, name='create_post_ajax'),
    path('ajax/edit-post/<int:post_id>/', views.edit_post_ajax, name='edit_post_ajax'),
    path('ajax/delete-post/<int:post_id>/', views.delete_post_ajax, name='delete_post_ajax'),

    # For Comments (All on the detail page)
    path('ajax/create-comment/<int:post_id>/', views.create_comment_ajax, name='create_comment_ajax'),
    path('ajax/edit-comment/<int:comment_id>/', views.edit_comment_ajax, name='edit_comment_ajax'),
    path('ajax/delete-comment/<int:comment_id>/', views.delete_comment_ajax, name='delete_comment_ajax'),
]