from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(
        upload_to='profile_pics/',  
        blank=True,                 
        null=True                   
    )

    strikes = models.IntegerField(default=0)

    @property
    def role(self):
        if self.is_superuser or self.is_staff:
            return "Admin"

        if self.groups.filter(name='Writers').exists():
            return "Writer"

        return "Reader"

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        if self.strikes >= 3 and not self.is_superuser:
            self.is_active = False

        super().save(*args, **kwargs)
