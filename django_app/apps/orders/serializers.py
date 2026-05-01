from rest_framework import serializers
from decimal import Decimal
from django.db import transaction
from apps.catalog.models import Product
from apps.orders.models import Order, OrderItem
from django.contrib.auth import get_user_model


class CartItemInputSerializer(serializers.Serializer):
    product_postgres_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, max_value=100)


class CheckoutValidateSerializer(serializers.Serializer):
    user_id = serializers.CharField()
    items = CartItemInputSerializer(many=True)
    shipping_address_id = serializers.IntegerField(required=False, allow_null=True)
    billing_address_id = serializers.IntegerField(required=False, allow_null=True)

    def validate_items(self, items):
        if not items:
            raise serializers.ValidationError("Le panier est vide.")
        return items

    def validate(self, data):
        items = data.get("items", [])
        errors = []
        stock_issues = []
        subtotal = Decimal("0")
        tax_amount = Decimal("0")

        for item in items:
            try:
                product = Product.objects.get(id=item["product_postgres_id"], is_active=True)
            except Product.DoesNotExist:
                errors.append(f"Produit ID {item['product_postgres_id']} non trouvé ou inactif")
                continue

            available = product.stock_quantity - product.stock_reserved
            if item["quantity"] > available:
                stock_issues.append({"sku": product.sku, "requested": item["quantity"], "available": available})

            line_ht = product.price * item["quantity"]
            line_tax = line_ht * product.tax_rate
            subtotal += line_ht
            tax_amount += line_tax

        data["summary"] = {
            "valid": len(errors) == 0 and len(stock_issues) == 0,
            "errors": errors,
            "stock_issues": stock_issues,
            "subtotal": subtotal,
            "tax_amount": tax_amount,
            "shipping_cost": Decimal("0.00"),
            "total_amount": subtotal + tax_amount,
            "total_items": sum(i["quantity"] for i in items),
        }
        return data


class CheckoutCreateSerializer(serializers.Serializer):
    user_id = serializers.CharField()
    items = CartItemInputSerializer(many=True)
    shipping_address_id = serializers.IntegerField(required=False, allow_null=True)
    billing_address_id = serializers.IntegerField(required=False, allow_null=True)

    def validate_items(self, items):
        if not items:
            raise serializers.ValidationError("Le panier est vide.")
        return items

    def create(self, validated_data):
        User = get_user_model()
        user = User.objects.get(id=int(validated_data["user_id"]))
        items = validated_data["items"]

        with transaction.atomic():
            subtotal = Decimal("0")
            tax_amount = Decimal("0")
            order_items_data = []

            for item in items:
                product = Product.objects.select_for_update().get(id=item["product_postgres_id"])
                available = product.stock_quantity - product.stock_reserved
                if item["quantity"] > available:
                    raise serializers.ValidationError(f"Stock insuffisant pour {product.sku} (dispo: {available})")

                product.stock_reserved += item["quantity"]
                product.save(update_fields=["stock_reserved"])

                line_ht = product.price * item["quantity"]
                line_tax = line_ht * product.tax_rate
                subtotal += line_ht
                tax_amount += line_tax
                order_items_data.append(
                    {
                        "product": product,
                        "quantity": item["quantity"],
                        "product_name": product.name,
                        "product_sku": product.sku,
                        "unit_price_ht": product.price,
                        "tax_rate": product.tax_rate,
                        "line_total_ht": line_ht,
                    }
                )

            total_amount = subtotal + tax_amount

            order = Order.objects.create(
                user=user,
                order_number="",
                status="pending",
                billing_address_id=validated_data.get("billing_address_id"),
                shipping_address_id=validated_data.get("shipping_address_id"),
                subtotal=subtotal,
                tax_amount=tax_amount,
                shipping_cost=Decimal("0.00"),
                total_amount=total_amount,
            )
            order.order_number = f"CMD-2026-{order.id:06d}"
            order.save(update_fields=["order_number"])

            for item_data in order_items_data:
                OrderItem.objects.create(order=order, **item_data)

            return order
