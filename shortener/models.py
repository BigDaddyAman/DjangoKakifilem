from django.db import models
import string
import random

def generate_short_id(length=6):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

class ShortURL(models.Model):
    short_id = models.CharField(max_length=10, unique=True, db_index=True)
    long_url = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    access_count = models.IntegerField(default=0)
    
    def save(self, *args, **kwargs):
        if not self.short_id:
            self.short_id = generate_short_id()
        super().save(*args, **kwargs)
