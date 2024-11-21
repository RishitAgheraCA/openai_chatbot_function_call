from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from .controller import (
    GenerateTokenAPI,
    InvalidateTokenAPI,
    TextAudioAPI,
    LoginAPI
)

urlpatterns = [
    path('generate-token/<str:browser_id>/', GenerateTokenAPI.as_view(), name='generate-token'),
    path('invalidate-token/', InvalidateTokenAPI.as_view()),
    path('text-audio/', TextAudioAPI.as_view(), name='text-audio'),
    path('login/', LoginAPI.as_view(), name='login'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
