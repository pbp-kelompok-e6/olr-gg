from django.contrib import admin
from .models import News

from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget
from users.models import CustomUser  

class NewsResource(resources.ModelResource):

    user = fields.Field(
        column_name='user',
        attribute='user',
        widget=ForeignKeyWidget(CustomUser, field='id')
    )

    class Meta:
        model = News
        fields = ('id', 'title', 'content', 'category', 'thumbnail', 'is_featured', 'user')
        import_id_fields = ('id',)
        skip_unchanged = True
        report_skipped = True


class NewsAdmin(ImportExportModelAdmin):
    resource_class = NewsResource

    list_display = ('title', 'category', 'is_featured', 'user', 'created_at')
    list_filter = ('category', 'is_featured', 'created_at')
    search_fields = ('title', 'content')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        
        if request.user.is_superuser:
            return qs 
        
        return qs.filter(user=request.user) 

    def save_model(self, request, obj, form, change):
        if not change:
            obj.user = request.user
        super().save_model(request, obj, form, change)


admin.site.register(News, NewsAdmin)