from django.urls import path

from ai_updater.views import AIResumeUpdateView

urlpatterns = [
    path("update/", AIResumeUpdateView.as_view(), name="ai-resume-update"),
]
