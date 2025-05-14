from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Item, Cart, CartItem, Payment, Sale

# Customize the User admin
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'is_seller', 'is_buyer', 'is_staff')
    list_filter = ('is_seller', 'is_buyer', 'is_staff', 'is_superuser')
    fieldsets = UserAdmin.fieldsets + (
        ('User Type', {'fields': ('is_seller', 'is_buyer')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('User Type', {'fields': ('is_seller', 'is_buyer')}),
    )

# Register the custom User model
admin.site.register(User, CustomUserAdmin)

# Register other models
admin.site.register(Item)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Payment)
admin.site.register(Sale)
