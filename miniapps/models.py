from django.db import models


class BugReport(models.Model):
    user_id = models.BigIntegerField()
    title = models.CharField(max_length=100)
    description = models.TextField()
    status = models.CharField(max_length=20, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'bug_reports'
        
    def __str__(self):
        return f"Bug #{self.id} - {self.title}"


class MovieRequest(models.Model):
    user_id = models.BigIntegerField()
    movie_name = models.CharField(max_length=255)
    additional_info = models.TextField(blank=True)
    status = models.CharField(max_length=20, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'movie_requests'
        
    def __str__(self):
        return f"Request: {self.movie_name}"


class VideoReport(models.Model):
    user_id = models.BigIntegerField()
    video_id = models.CharField(max_length=100)
    reason = models.TextField()
    status = models.CharField(max_length=20, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'video_reports'
        
    def __str__(self):
        return f"Video Report #{self.id}"


class BotNews(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'bot_news'
        ordering = ['-created_at']
        
    def __str__(self):
        return self.title


class PremiumStatus(models.Model):
    user_id = models.BigIntegerField(unique=True)
    start_date = models.DateTimeField()
    expiry_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'premium_status'
        
    def __str__(self):
        return f"Premium Status for User {self.user_id}"
