from django.urls import path

from ai_updater import views

urlpatterns = [
    path("update-resume/", views.update_resume, name="ai-update-resume"),
]
