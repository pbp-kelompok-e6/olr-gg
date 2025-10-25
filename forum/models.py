# forum/models.py

from django.db import models
from users.models import CustomUser

CATEGORY_CHOICES = (
    ('soccer', 'Soccer'),
    ('basketball', 'Basketball'),
    ('football', 'Football'),
    ('hockey', 'Hockey'),
    ('volleyball', 'Volleyball'),
    ('baseball', 'Baseball'),
)

# model untuk post di forum
class ForumPost(models.Model):
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='soccer')

    def __str__(self):
        return self.title

# model untuk komentar pada post 
class ForumComment(models.Model):
    post = models.ForeignKey(ForumPost, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Comment by {self.author.username} on {self.post.title}'