from apps.cart.cart import SessionCart


def cart(request):
    try:
        session_cart = SessionCart(request)
        return {"cart_count": len(session_cart)}
    except Exception:
        return {"cart_count": 0}
