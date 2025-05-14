from .models import Cart

def cart_processor(request):
    """
    Context processor to add the active cart to all templates
    """
    if request.user.is_authenticated and request.user.is_buyer:
        cart = Cart.get_cart_for_user(request.user)
        return {
            'active_cart': cart,
            'cart_quantity': cart.total_quantity() if cart and cart.items.exists() else 0
        }
    return {
        'active_cart': None,
        'cart_quantity': 0
    }
