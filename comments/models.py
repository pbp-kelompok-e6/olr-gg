import uuid
from django.db import models
from users.models import CustomUser;
from berita.models import News;

# Create your models here.
class Comments(models.Model):
    news = models.ForeignKey(News, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null = True, blank = True)
    
    def __str__(self):
        return self.content
    
