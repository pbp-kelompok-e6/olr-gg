import uuid
from django.db import models
from django.conf import settings

<<<<<<< HEAD
# Create your models here.
class News(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True) 
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
=======
# Create your models here.
>>>>>>> 9ea3b7cda7011206d29da9fba57294f9e09871f3
