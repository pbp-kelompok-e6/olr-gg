# model untuk app rating
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from berita.models import News
from users.models import CustomUser

class Rating(models.Model):
    news = models.ForeignKey(News, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    review = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('news', 'user')  # Satu user cuma bisa review sekali per berita