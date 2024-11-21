from django.db import models
from .BaseModel import BaseModel
from django.utils import timezone

class ChatSession(models.Model, BaseModel):
    browser_id = models.CharField(max_length=256)  # Browser identifier (generated on the frontend)
    created_at = models.DateTimeField(auto_now_add=True)  # Session creation timestamp
    ended_at = models.DateTimeField(null=True, blank=True)  # Session end timestamp (null if still active)
    is_active = models.BooleanField(default=True)  # Status of the session (active/inactive)

    thread_id = models.CharField(max_length=256, null=True, blank=True)  # OpenAI thread identifier


    def expire_session(self):
        self.is_active = False
        self.ended_at = timezone.now()
        self.save()

    def __str__(self):
        return f"{self.browser_id} - {self.thread_id} - {self.is_active}"