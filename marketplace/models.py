from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

# Extend the default User model
class User(AbstractUser):
    is_seller = models.BooleanField(default=False)
    is_buyer = models.BooleanField(default=False)

# Livestock or Poultry Item
class Item(models.Model):
    SELL_CATEGORY = (
        ('livestock', 'Livestock'),
        ('poultry', 'Poultry'),
    )

    seller = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'is_seller': True})
    name = models.CharField(max_length=100)
    description = models.TextField()
    category = models.CharField(max_length=10, choices=SELL_CATEGORY)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    available = models.BooleanField(default=True)
    image = models.ImageField(upload_to='item_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.category}"

    def get_category_display(self):
        return dict(self.SELL_CATEGORY).get(self.category, self.category)

# Cart model
class Cart(models.Model):
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'is_buyer': True})
    created_at = models.DateTimeField(auto_now_add=True)
    available = models.BooleanField(default=True)

    def total_price(self):
        return sum(item.total_price() for item in self.items.all())

    def total_quantity(self):
        """Return the total quantity of all items in the cart"""
        if not self.available:
            return 0
        return sum(item.quantity for item in self.items.all())

    @classmethod
    def get_cart_for_user(cls, user):
        """Get or create a cart for a user"""
        if not user.is_authenticated or not user.is_buyer:
            return None

        try:
            # First, mark all unavailable carts as unavailable
            cls.objects.filter(buyer=user, available=False).update(available=False)

            # Get all available carts
            carts = cls.objects.filter(buyer=user, available=True)

            if carts.count() > 1:
                # Keep the most recent cart and mark others as unavailable
                latest_cart = carts.order_by('-created_at').first()
                carts.exclude(id=latest_cart.id).update(available=False)
                return latest_cart
            elif carts.exists():
                return carts.first()
            else:
                # Create a new cart if none exists
                return cls.objects.create(buyer=user, available=True)
        except Exception:
            # Fallback if available field doesn't exist yet
            carts = cls.objects.filter(buyer=user)
            if carts.count() > 1:
                # Keep the most recent cart
                latest_cart = carts.order_by('-created_at').first()
                # We can't update available, so just return the latest cart
                return latest_cart
            elif carts.exists():
                return carts.first()
            else:
                # Create a new cart if none exists
                return cls.objects.create(buyer=user)

# Cart Item
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def total_price(self):
        return self.item.price * self.quantity

# Payment with GCash proof
class Payment(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    cart = models.OneToOneField(Cart, on_delete=models.CASCADE)
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    gcash_reference = models.CharField(max_length=100)
    proof_screenshot = models.ImageField(upload_to='gcash_proofs/')
    paid_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    verified = models.BooleanField(default=False)  # Keeping for backward compatibility
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_payments')
    approved_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Payment {self.id} - {self.gcash_reference} ({self.status})"

    def get_items_by_seller(self, seller):
        """Get items in this payment that belong to a specific seller"""
        return CartItem.objects.filter(
            cart=self.cart,
            item__seller=seller
        )

# Sales Record (for admin or seller reporting)
class Sale(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    buyer = models.ForeignKey(User, on_delete=models.CASCADE)
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sales', null=True, blank=True)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='sales', null=True, blank=True)
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    sold_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Sale of {self.item.name} to {self.buyer.username}"

# Notification model for sellers
class Notification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', limit_choices_to={'is_seller': True})
    message = models.CharField(max_length=255)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='notifications', null=True, blank=True)
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.recipient.username}: {self.message[:30]}..."

    def mark_as_read(self):
        self.read = True
        self.save()
