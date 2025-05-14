from .models import Cart, Notification

def cart_processor(request):
    """
    Context processor to add the active cart to all templates
    """
    if request.user.is_authenticated and request.user.is_buyer:
        cart = Cart.get_cart_for_user(request.user)
        # Use total_quantity method to get the correct count
        cart_quantity = cart.total_quantity() if cart else 0
        return {
            'active_cart': cart,
            'cart': cart,  # Add cart directly for templates that use cart.items.count
            'cart_quantity': cart_quantity
        }
    return {
        'active_cart': None,
        'cart': None,
        'cart_quantity': 0
    }

def notification_processor(request):
    """
    Context processor to add notifications for sellers
    """
    if request.user.is_authenticated and request.user.is_seller:
        # Get unread notifications count
        unread_count = Notification.objects.filter(recipient=request.user, read=False).count()
        # Get recent notifications (limit to 5)
        recent_notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')[:5]

        return {
            'unread_notifications_count': unread_count,
            'recent_notifications': recent_notifications
        }
    return {
        'unread_notifications_count': 0,
        'recent_notifications': []
    }
