"""Session cart — stores only variant_id → qty (never prices)."""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from django.shortcuts import get_object_or_404

from apps.catalog.models import Availability, ProductVariant

CART_SESSION_KEY = "cart"


@dataclass
class CartLine:
    variant: ProductVariant
    quantity: int

    @property
    def unit_price(self) -> Decimal:
        return self.variant.price

    @property
    def line_total(self) -> Decimal:
        return self.unit_price * self.quantity


class SessionCart:
    def __init__(self, request):
        self.request = request
        self.session = request.session
        cart = self.session.get(CART_SESSION_KEY)
        if not isinstance(cart, dict):
            cart = {}
        self._cart: dict[str, int] = {str(k): int(v) for k, v in cart.items() if int(v) > 0}

    def save(self) -> None:
        self.session[CART_SESSION_KEY] = self._cart
        self.session.modified = True

    def clear(self) -> None:
        self._cart = {}
        self.save()

    @staticmethod
    def _assert_stock_allows(variant: ProductVariant, quantity: int) -> None:
        """IN_STOCK lines cannot exceed warehouse stock; ON_ORDER has no hard cap."""
        if quantity <= 0:
            return
        if not variant.is_purchasable:
            raise ValueError("Variant is not purchasable")
        if (
            variant.effective_availability() == Availability.IN_STOCK
            and quantity > variant.stock
        ):
            raise ValueError("Quantity exceeds stock")

    def _get_purchasable_variant(self, variant_id: int | str) -> ProductVariant:
        variant = get_object_or_404(
            ProductVariant.objects.select_related("product"),
            pk=variant_id,
            is_active=True,
            product__is_active=True,
        )
        if not variant.is_purchasable:
            raise ValueError("Variant is not purchasable")
        return variant

    def add(self, variant_id: int | str, quantity: int = 1) -> ProductVariant:
        variant = self._get_purchasable_variant(variant_id)
        key = str(variant.pk)
        new_qty = self._cart.get(key, 0) + max(1, int(quantity))
        self._assert_stock_allows(variant, new_qty)
        self._cart[key] = new_qty
        self.save()
        return variant

    def set_qty(self, variant_id: int | str, quantity: int) -> None:
        key = str(variant_id)
        qty = int(quantity)
        if qty <= 0:
            self._cart.pop(key, None)
            self.save()
            return
        if key not in self._cart:
            return
        variant = self._get_purchasable_variant(variant_id)
        self._assert_stock_allows(variant, qty)
        self._cart[key] = qty
        self.save()

    def remove(self, variant_id: int | str) -> None:
        self._cart.pop(str(variant_id), None)
        self.save()

    def __len__(self) -> int:
        return sum(self._cart.values())

    def lines(self) -> list[CartLine]:
        if not self._cart:
            return []
        variants = {
            str(v.pk): v
            for v in ProductVariant.objects.filter(
                pk__in=self._cart.keys(),
                is_active=True,
                product__is_active=True,
            )
            .select_related("product")
            .prefetch_related("product__images")
        }
        result: list[CartLine] = []
        stale: list[str] = []
        for key, qty in self._cart.items():
            variant = variants.get(key)
            if not variant:
                stale.append(key)
                continue
            result.append(CartLine(variant=variant, quantity=qty))
        if stale:
            for key in stale:
                self._cart.pop(key, None)
            self.save()
        return result

    @property
    def total(self) -> Decimal:
        return sum((line.line_total for line in self.lines()), Decimal("0"))

    def is_empty(self) -> bool:
        return len(self) == 0
