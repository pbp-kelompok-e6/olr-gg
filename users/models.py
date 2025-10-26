# model untuk app users
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

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

class Report(models.Model):
    # User yang membuat laporan
    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="reports_made"
    )
    
    # User yang dilaporkan
    reported_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="reports_received"
    )
    
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report by {self.reporter.username} against {self.reported_user.username}"