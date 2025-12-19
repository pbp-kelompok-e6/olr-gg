from django.urls import path
from comments import views
from .views import edit_profile, report_user, show_profile, load_news, change_profile_pic, admin_dashboard, admin_edit_user, admin_reset_strikes, admin_delete_report
from .views import admin_accept_report, request_writer_role, admin_approve_writer, admin_reject_writer, show_current_user_profile, edit_profile_flutter
from .views import request_writer_role_flutter
app_name = 'users'

urlpatterns = [
    path('edit_profile/', edit_profile, name='edit_profile'),
    path('edit_profile_flutter/', edit_profile_flutter, name='edit_profile_flutter'),
    path('show_profile/<int:id>/', show_profile, name='show_profile'),
    path('load_news/', load_news, name='load_news'),
    path('change_pic', change_profile_pic, name='change_pic'),
    path('report_user/<int:id>/', report_user, name='report_user'),
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard/edit-user/<int:id>/', admin_edit_user, name='admin_edit_user'),
    path('admin-dashboard/reset-strikes/<int:id>/', admin_reset_strikes, name='admin_reset_strikes'),
    path('admin-dashboard/delete-report/<int:id>/', admin_delete_report, name='admin_delete_report'),
    path('admin-dashboard/accept-report/<int:id>/', admin_accept_report, name='admin_accept_report'),
    path('request-writer-role/', request_writer_role, name='request_writer_role'),
    path('admin-dashboard/approve-writer/<int:id>/', admin_approve_writer, name='admin_approve_writer'),
    path('admin-dashboard/reject-writer/<int:id>/', admin_reject_writer, name='admin_reject_writer'),
    path('api/profile/', show_current_user_profile, name='api_profile'),    
    path('api/request-writer-role/', request_writer_role_flutter, name='request_writer_role_flutter'),
]