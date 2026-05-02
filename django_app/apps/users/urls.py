from django.urls import path
from .views import (
    RegisterView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
    UserProfileView,
    UserOrdersView,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("reset-request/", PasswordResetRequestView.as_view(), name="reset-request"),
    path("reset-confirm/", PasswordResetConfirmView.as_view(), name="reset-confirm"),
    path("profile/", UserProfileView.as_view(), name="profile"),
    path("orders/", UserOrdersView.as_view(), name="user-orders"),
]
