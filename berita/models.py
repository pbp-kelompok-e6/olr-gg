import uuid
from django.db import models
from django.db.models import Avg
from users.models import CustomUser

class News(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)
    SPORTS_CHOICES = [
        ('basketball', 'Basketball'),
        ('soccer', 'Soccer'),
        ('football', 'Football'),
        ('hockey', 'Hockey'),
        ('voleyball', 'Voleyball'),
        ('baseball', 'Baseball'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    content = models.TextField()
    category = models.CharField(max_length=20, choices=SPORTS_CHOICES, default='update')
    thumbnail = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_featured = models.BooleanField(default=False)

    def __str__(self):
        return self.title
    
    @property
    def average_rating(self):
        from rating.models import Rating  
        result = Rating.objects.filter(news=self).aggregate(avg=Avg('rating'))
        avg_value = result['avg']
        return round(avg_value, 1) if avg_value else None