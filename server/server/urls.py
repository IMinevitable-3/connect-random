from django.contrib import admin
from django.urls import path
from rest_api import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/issue-token", views.IssueToken.as_view()),
    path("api/pair-me", views.AddToQueue.as_view()),
]
