from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    # API Core v1 (Auth, Checkout, Utilisateurs)
    path("api/v1/auth/", include("apps.accounts.urls")),
    path("api/v1/orders/", include("apps.orders.urls")),
    # Les routes api/v1/users viendront en Phase 9
]