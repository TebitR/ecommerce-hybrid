from django.contrib import admin
from .models import Order, OrderItem, Invoice, Payment

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ("line_total_ht",)
    extra = 0
    can_delete = False

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("order_number", "user", "status", "total_amount", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("order_number", "user__username", "user__email")
    inlines = [OrderItemInline]
    readonly_fields = ("created_at", "paid_at", "shipped_at", "subtotal", "tax_amount", "total_amount")
    list_per_page = 15
    ordering = ("-created_at",)
    verbose_name = "Commande"
    verbose_name_plural = "Commandes"

    actions = ["mark_as_paid", "mark_as_shipped"]

    def mark_as_paid(self, request, queryset):
        from django.utils import timezone
        queryset.update(status="paid", paid_at=timezone.now())
        self.message_user(request, f"{queryset.count()} commande(s) marquée(s) payée(s).")
    mark_as_paid.short_description = "Marquer comme payée"

    def mark_as_shipped(self, request, queryset):
        from django.utils import timezone
        queryset.update(status="shipped", shipped_at=timezone.now())
        self.message_user(request, f"{queryset.count()} commande(s) marquée(s) expédiée(s).")
    mark_as_shipped.short_description = "Marquer comme expédiée"

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("invoice_number", "order", "issued_at", "pdf_path")
    readonly_fields = ("issued_at",)
    verbose_name = "Facture"
    verbose_name_plural = "Factures"

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("transaction_id", "order", "provider", "amount", "status", "created_at")
    list_filter = ("status", "provider")
    readonly_fields = ("created_at", "payload")
    verbose_name = "Paiement"
    verbose_name_plural = "Paiements"
