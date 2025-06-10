from django.db import models
from django.utils import timezone
import json

class UserSession(models.Model):
    whatsapp_id = models.CharField(max_length=100, unique=True)
    user_type = models.CharField(max_length=20, choices=[
        ('patient', 'Patient'),
        ('staff', 'Hospital Staff'),
        ('unknown', 'Unknown')
    ], default='unknown')
    current_state = models.CharField(max_length=50, default='new')
    session_data = models.JSONField(default=dict)
    is_authenticated = models.BooleanField(default=False)
    auth_token = models.TextField(blank=True, null=True)
    last_activity = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_sessions'

    def __str__(self):
        return f"{self.whatsapp_id} - {self.user_type} - {self.current_state}"

    def update_session(self, state=None, data=None):
        if state:
            self.current_state = state
        if data:
            self.session_data.update(data)
        self.last_activity = timezone.now()
        self.save()

    def is_session_expired(self, timeout_minutes=30):
        time_diff = timezone.now() - self.last_activity
        return time_diff.total_seconds() > (timeout_minutes * 60)

    def clear_session(self):
        self.current_state = 'new'
        self.session_data = {}
        self.is_authenticated = False
        self.auth_token = None
        self.save()

class BotMessage(models.Model):
    session = models.ForeignKey(UserSession, on_delete=models.CASCADE)
    message_type = models.CharField(max_length=20, choices=[
        ('incoming', 'Incoming'),
        ('outgoing', 'Outgoing')
    ])
    message_content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'bot_messages'
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.session.whatsapp_id} - {self.message_type} - {self.timestamp}"
