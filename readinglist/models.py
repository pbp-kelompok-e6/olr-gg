import uuid
from django.db import models
from django.conf import settings
from berita.models import News 
from users.models import CustomUser

# Model untuk List Bacaan (Folder)
class ReadingList(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s List: {self.name}"

# Model untuk Item Berita di dalam List
class ReadingListItem(models.Model):
    # Foreign key ke list mana item ini berada
    list = models.ForeignKey(ReadingList, on_delete=models.CASCADE, related_name='items') 
    # Foreign key ke berita yang disimpan
    news = models.ForeignKey(News, on_delete=models.CASCADE) 
    added_at = models.DateTimeField(auto_now_add=True)
    
    # Fitur Status Baca
    is_read = models.BooleanField(default=False)

    class Meta:
        # Menetapkan urutan: 'is_read' (False/Belum dibaca lebih dulu), lalu '-added_at' (terbaru lebih dulu)
        ordering = ['is_read', '-added_at'] 
        # Memastikan satu berita hanya dapat ditambahkan sekali ke satu list
        unique_together = ('list', 'news') 

    def __str__(self):
        return f"{self.news.id} in {self.list.name}"