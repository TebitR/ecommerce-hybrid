from django.contrib import admin
from django.urls import path

urlpatterns = [
    path("admin/", admin.site.urls),
    # Les routes API v1 (Django REST) seront ajoutées en Phase 4
]
