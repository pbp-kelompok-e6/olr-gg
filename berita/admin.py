from django.contrib import admin
from .models import News

class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'is_featured', 'user', 'created_at')
    list_filter = ('category', 'is_featured', 'created_at')
    search_fields = ('title', 'content')

    # Metode ini akan memfilter news berdasarkan user yang membuatnya.
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        
        # --- PERBAIKAN UTAMA DI SINI ---
        # Superuser (Admin) dapat melihat SEMUA berita.
        # Pengguna biasa hanya dapat melihat berita yang mereka buat.
        if request.user.is_superuser:
            return qs # Mengembalikan SEMUA objek jika superuser
        
        return qs.filter(user=request.user) # Filter jika bukan superuser
        # --- AKHIR PERBAIKAN ---

    def save_model(self, request, obj, form, change):
        # Otomatis mengisi kolom 'user' saat berita pertama kali dibuat
        if not change:
            obj.user = request.user
        super().save_model(request, obj, form, change)

admin.site.register(News, NewsAdmin)
