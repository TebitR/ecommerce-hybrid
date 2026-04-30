from django.contrib.auth.models import User
from django.db import models

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    phone = models.CharField(max_length=20, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profil de {self.user.username}"

class Address(models.Model):
    TYPE_CHOICES = [("livraison", "Livraison"), ("facturation", "Facturation")]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="addresses")
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=2, default="FR")
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.type.capitalize()} - {self.city}"
