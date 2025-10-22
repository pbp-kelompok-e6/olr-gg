import uuid
from django.db import models
from django.conf import settings

# Create your models here.
class News(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True) 
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    