from django.contrib import admin
from .models import Category, Product

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "parent", "is_active", "created_at")
    list_filter = ("is_active", "parent")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    list_per_page = 25
    ordering = ("name",)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("sku", "name", "category", "price", "stock_quantity", "is_active", "created_at")
    list_filter = ("is_active", "category", "created_at")
    search_fields = ("sku", "name", "category__name")
    prepopulated_fields = {}  # Le slug est géré dans MongoDB, pas ici
    list_per_page = 20
    ordering = ("name",)
    readonly_fields = ("created_at", "updated_at")
    fields = (
        "sku",
        "name",
        "category",
        "price",
        "tax_rate",
        "stock_quantity",
        "stock_reserved",
        "is_active",
        "image",
        "mongo_id",
        "created_at",
        "updated_at",
    )

    # Actions bulk
    actions = ["mark_active", "mark_inactive", "sync_to_mongo"]

    def mark_active(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f"{queryset.count()} produit(s) activé(s).")
    mark_active.short_description = "Activer les produits sélectionnés"

    def mark_inactive(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f"{queryset.count()} produit(s) désactivé(s).")
    mark_inactive.short_description = "Désactiver les produits sélectionnés"

    def sync_to_mongo(self, request, queryset):
        from .tasks import sync_product_to_mongo

        count = 0
        for product in queryset:
            sync_product_to_mongo.delay(product.id)
            count += 1
        self.message_user(request, f"{count} produit(s) envoyés en synchro MongoDB.")

    sync_to_mongo.short_description = "Forcer la synchronisation vers MongoDB"
