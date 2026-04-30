from django.contrib.auth.models import User
from django.db import models
from apps.catalog.models import Product
from apps.accounts.models import Address

class Order(models.Model):
    STATUS_CHOICES = [("pending", "En attente"), ("paid", "Payée"), ("preparing", "En préparation"), 
                      ("shipped", "Expédiée"), ("delivered", "Livrée"), ("cancelled", "Annulée")]
    order_number = models.CharField(max_length=50, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="pending")
    billing_address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True, related_name="billing_orders")
    shipping_address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True, related_name="shipping_orders")
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    paid_at = models.DateTimeField(null=True, blank=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Commande {self.order_number}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=500)
    product_sku = models.CharField(max_length=100)
    unit_price_ht = models.DecimalField(max_digits=12, decimal_places=2)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=4)
    quantity = models.PositiveIntegerField()
    line_total_ht = models.DecimalField(max_digits=12, decimal_places=2)

class Invoice(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="invoice")
    invoice_number = models.CharField(max_length=50, unique=True)
    pdf_path = models.CharField(max_length=512, blank=True, null=True)
    issued_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField(blank=True, null=True)

class Payment(models.Model):
    PROVIDER_CHOICES = [("stripe", "Stripe"), ("paypal", "PayPal"), ("manual", "Manuel")]
    STATUS_CHOICES = [("success", "Succès"), ("failed", "Échec"), ("refunded", "Remboursé"), ("pending", "En attente")]
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="payments")
    provider = models.CharField(max_length=50, choices=PROVIDER_CHOICES)
    transaction_id = models.CharField(max_length=200, unique=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default="EUR")
    status = models.CharField(max_length=30, choices=STATUS_CHOICES)
    payload = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
