from django.contrib import admin
from users.models import CustomUser, Report
from django.contrib.auth.admin import UserAdmin


class CustomUserAdmin(UserAdmin):
    readonly_fields = ('id',)  

    fieldsets = (
        (None, {'fields': ('id', 'username', 'password')}), 
        ('Informasi Pribadi', {'fields': ('first_name', 'last_name', 'email', 'bio', 'profile_picture')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions', 'strikes')}),
        ('Tanggal Penting', {'fields': ('last_login', 'date_joined')}),
        
    )

    list_display = ('id', 'username', 'email', 'is_staff', 'strikes')

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    """
    Kustomisasi admin panel untuk me-review laporan.
    """
    list_display = ('reported_user', 'reporter', 'reason', 'get_created_at')
    list_filter = ('reason', 'reported_user__username', 'reporter__username')
    search_fields = ('reported_user__username', 'reporter__username', 'reason')
    
    readonly_fields = [field.name for field in Report._meta.fields]

    def get_created_at(self, obj):
        # Asumsi model Report Anda punya field 'created_at'
        if hasattr(obj, 'created_at'):
            return obj.created_at.strftime("%Y-%m-%d %H:%M")
        return None
    get_created_at.short_description = 'Waktu Laporan'

    def has_add_permission(self, request):
        # Admin tidak boleh membuat laporan dari admin panel
        return False

    def has_delete_permission(self, request, obj=None):
        # Izinkan admin menghapus laporan jika perlu (misal: spam report)
        return True
    
    def delete_model(self, request, obj):
        user_to_pardon = obj.reported_user
        
        # Panggil fungsi delete asli
        super().delete_model(request, obj)
        
        # Kurangi strike
        if user_to_pardon and user_to_pardon.strikes > 0:
            user_to_pardon.strikes -= 1
            user_to_pardon.save()

    # FUNGSI 2: Dipanggil saat delete MASSAL (dari halaman list)
    def delete_queryset(self, request, queryset):
        # 1. Kumpulkan dulu siapa saja yang strike-nya mau dikurangi
        #    Kita pakai dict agar efisien: {user_obj: jumlah_laporan_dihapus}
        user_strike_counts = {}
        for report in queryset:
            user = report.reported_user
            if user in user_strike_counts:
                user_strike_counts[user] += 1
            else:
                user_strike_counts[user] = 1

        # 2. Panggil fungsi delete aslinya untuk menghapus laporan
        super().delete_queryset(request, queryset)

        # 3. Update strike count untuk setiap user yang terpengaruh
        for user, count_to_reduce in user_strike_counts.items():
            if user.strikes >= count_to_reduce:
                user.strikes -= count_to_reduce
            else:
                user.strikes = 0  # Pastikan tidak negatif
            user.save()

admin.site.register(CustomUser, CustomUserAdmin)

