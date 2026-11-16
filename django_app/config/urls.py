from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    # API Core v1 (Auth, Checkout, Utilisateurs)
    path("api/v1/auth/", include("apps.accounts.urls")),
    path("api/v1/orders/", include("apps.orders.urls")),
    path("api/v1/users/", include("apps.users.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)