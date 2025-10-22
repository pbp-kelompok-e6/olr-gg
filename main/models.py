import uuid
from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class News(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True) 
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)