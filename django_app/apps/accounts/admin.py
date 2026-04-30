from django.contrib import admin
from .models import UserProfile, Address

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "phone", "birth_date", "created_at")
    search_fields = ("user__username", "user__email", "phone")
    readonly_fields = ("created_at", "updated_at")
    verbose_name = "Profil Utilisateur"
    verbose_name_plural = "Profils Utilisateurs"

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ("user", "type", "city", "postal_code", "is_default")
    list_filter = ("type", "is_default")
    search_fields = ("user__username", "city", "postal_code")
    verbose_name = "Adresse"
    verbose_name_plural = "Adresses"
