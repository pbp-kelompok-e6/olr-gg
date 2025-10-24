from django.contrib import admin
from users.models import CustomUser
from django.contrib.auth.admin import UserAdmin
# Register your models here.


class CustomUserAdmin(UserAdmin):
    readonly_fields = ('id',)  

    fieldsets = (
        (None, {'fields': ('id', 'username', 'password')}), 
        ('Informasi Pribadi', {'fields': ('first_name', 'last_name', 'email', 'bio', 'profile_picture')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions', 'strikes')}),
        ('Tanggal Penting', {'fields': ('last_login', 'date_joined')}),
        
        # Jika Anda menambahkan field kustom (misal: bio, profile_picture)
        # ('Informasi Profil Kustom', {'fields': ('bio', 'profile_picture')}),
    )

    # ... (list_display, filter, search, dll.)
    list_display = ('id', 'username', 'email', 'is_staff', 'strikes')

admin.site.register(CustomUser, CustomUserAdmin)