# model untuk app users
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('writer', 'Writer'),
        ('reader', 'Reader'),
        ('admin', 'Admin'),
    ]

    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(
        upload_to='profile_pics/',  
        blank=True,                 
        null=True                   
    )

    strikes = models.IntegerField(default=0)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='reader')

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        if self.pk is None and self.is_superuser:
            self.role = 'admin'
            
        if self.role == 'admin':
            self.is_staff = True
            self.is_superuser = True
        else:
            self.is_staff = False
            self.is_superuser = False 
        
        if self.is_superuser:
            self.is_staff = True
            self.role = 'admin'
            self.is_active = True
        else:
            if self.strikes >= 3:
                self.is_active = False
            else:
                self.is_active = True  

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