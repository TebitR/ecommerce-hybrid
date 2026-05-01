from django.urls import path
from .views import CheckoutValidateView, CheckoutCreateView
urlpatterns = [
    path("validate/", CheckoutValidateView.as_view(), name="checkout_validate"),
    path("create/", CheckoutCreateView.as_view(), name="checkout_create"),
]
