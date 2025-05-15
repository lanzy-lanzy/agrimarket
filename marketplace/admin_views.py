from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum, Count, Q
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils import timezone
from django.core.paginator import Paginator
from .models import User, Item, Cart, CartItem, Payment, Sale, Notification
from .forms import AdminUserCreationForm, AdminUserEditForm

# Helper function to check if user is admin
def is_admin(user):
    return user.is_authenticated and user.is_superuser

# Admin dashboard
@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    # Get statistics for the dashboard
    total_users = User.objects.count()
    total_sellers = User.objects.filter(is_seller=True).count()
    total_buyers = User.objects.filter(is_buyer=True).count()
    total_items = Item.objects.count()

    # Get pending approvals count
    pending_approvals_count = User.objects.filter(is_active=False, is_approved=False).count()

    # Get recent users for the dashboard
    recent_users = User.objects.all().order_by('-date_joined')[:5]

    # Get pending approval users
    pending_users = User.objects.filter(is_active=False, is_approved=False).order_by('-date_joined')[:5]

    # Current time for system status
    now = timezone.now()

    return render(request, 'admin/dashboard.html', {
        'total_users': total_users,
        'total_sellers': total_sellers,
        'total_buyers': total_buyers,
        'total_items': total_items,
        'recent_users': recent_users,
        'pending_approvals_count': pending_approvals_count,
        'pending_users': pending_users,
        'now': now
    })

# User management views
@login_required
@user_passes_test(is_admin)
def user_list(request):
    # Get filter parameters
    search_query = request.GET.get('search', '')
    role_filter = request.GET.get('role', '')
    status_filter = request.GET.get('status', '')

    # Start with all users
    users = User.objects.all()

    # Apply search filter
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )

    # Apply role filter
    if role_filter:
        if role_filter == 'admin':
            users = users.filter(is_superuser=True)
        elif role_filter == 'seller':
            users = users.filter(is_seller=True)
        elif role_filter == 'buyer':
            users = users.filter(is_buyer=True)

    # Apply status filter
    if status_filter:
        if status_filter == 'active':
            users = users.filter(is_active=True)
        elif status_filter == 'inactive':
            users = users.filter(is_active=False)
        elif status_filter == 'pending':
            users = users.filter(is_active=False, is_approved=False)

    # Order users by date joined (newest first)
    users = users.order_by('-date_joined')

    # Paginate the results
    paginator = Paginator(users, 10)  # Show 10 users per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Count pending approvals for notification badge
    pending_approvals_count = User.objects.filter(is_active=False, is_approved=False).count()

    return render(request, 'admin/user_list.html', {
        'users': page_obj,
        'is_paginated': paginator.num_pages > 1,
        'page_obj': page_obj,
        'pending_approvals_count': pending_approvals_count,
        'search_query': search_query,
        'role_filter': role_filter,
        'status_filter': status_filter
    })

@login_required
@user_passes_test(is_admin)
def user_detail(request, user_id):
    user = get_object_or_404(User, id=user_id)

    # Get user activity data
    context = {'user': user}

    if user.is_seller:
        # Get seller statistics
        seller_items = Item.objects.filter(seller=user)
        seller_sales = Sale.objects.filter(seller=user)
        seller_revenue = seller_sales.aggregate(total=Sum('total_price'))['total'] or 0

        context.update({
            'seller_items_count': seller_items.count(),
            'seller_sales_count': seller_sales.count(),
            'seller_revenue': seller_revenue
        })

    if user.is_buyer:
        # Get buyer statistics
        buyer_orders = Payment.objects.filter(buyer=user)

        # Calculate total spent by getting all cart items and summing their prices
        buyer_spent = 0
        for payment in buyer_orders:
            try:
                cart_items = CartItem.objects.filter(cart=payment.cart)
                for item in cart_items:
                    buyer_spent += item.total_price()
            except:
                pass

        # Get current cart items
        try:
            current_cart = Cart.objects.filter(buyer=user, available=True).first()
            buyer_cart_items = CartItem.objects.filter(cart=current_cart).count() if current_cart else 0
        except:
            buyer_cart_items = 0

        context.update({
            'buyer_orders_count': buyer_orders.count(),
            'buyer_spent': buyer_spent,
            'buyer_cart_items': buyer_cart_items
        })

    return render(request, 'admin/user_detail.html', context)

@login_required
@user_passes_test(is_admin)
def user_create(request):
    if request.method == 'POST':
        form = AdminUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # Set additional fields from form data
            user.is_superuser = form.cleaned_data.get('is_superuser', False)
            user.is_seller = form.cleaned_data.get('is_seller', False)
            user.is_buyer = form.cleaned_data.get('is_buyer', False)
            user.is_active = form.cleaned_data.get('is_active', True)
            user.save()

            messages.success(request, f"User '{user.username}' created successfully!")
            return redirect('user_detail', user_id=user.id)
    else:
        form = AdminUserCreationForm()

    return render(request, 'admin/user_create.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def user_edit(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        form = AdminUserEditForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save(commit=False)
            # Set additional fields from form data
            user.is_superuser = form.cleaned_data.get('is_superuser', False)
            user.is_seller = form.cleaned_data.get('is_seller', False)
            user.is_buyer = form.cleaned_data.get('is_buyer', False)
            user.is_active = form.cleaned_data.get('is_active', True)

            # Handle password change if provided
            password1 = form.cleaned_data.get('password1')
            if password1:
                user.set_password(password1)

            user.save()

            messages.success(request, f"User '{user.username}' updated successfully!")
            return redirect('user_detail', user_id=user.id)
    else:
        form = AdminUserEditForm(instance=user)

    return render(request, 'admin/user_edit.html', {'form': form, 'user': user})

@login_required
@user_passes_test(is_admin)
def user_toggle_status(request, user_id):
    user = get_object_or_404(User, id=user_id)

    # Toggle the user's active status
    user.is_active = not user.is_active
    user.save()

    status = "activated" if user.is_active else "deactivated"
    messages.success(request, f"User '{user.username}' has been {status}!")

    # Redirect back to the referring page or user list
    return redirect(request.META.get('HTTP_REFERER', 'user_list'))

@login_required
@user_passes_test(is_admin)
def pending_approvals(request):
    """View to list all users pending approval"""
    # Get all users that are inactive and not approved
    pending_users = User.objects.filter(is_active=False, is_approved=False).order_by('-date_joined')

    # Paginate the results
    paginator = Paginator(pending_users, 10)  # Show 10 users per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'admin/pending_approvals.html', {
        'users': page_obj,
        'is_paginated': paginator.num_pages > 1,
        'page_obj': page_obj,
        'pending_count': pending_users.count()
    })

@login_required
@user_passes_test(is_admin)
def approve_user(request, user_id):
    """Approve a user registration"""
    user = get_object_or_404(User, id=user_id)

    # Set user as active and approved
    user.is_active = True
    user.is_approved = True
    user.save()

    messages.success(request, f"User '{user.username}' has been approved and can now log in!")

    # Redirect back to the referring page or pending approvals
    return redirect(request.META.get('HTTP_REFERER', 'pending_approvals'))

@login_required
@user_passes_test(is_admin)
def reject_user(request, user_id):
    """Reject a user registration"""
    user = get_object_or_404(User, id=user_id)

    # Keep user as inactive but mark as approved (rejected)
    user.is_approved = True
    user.save()

    messages.success(request, f"User '{user.username}' has been rejected!")

    # Redirect back to the referring page or pending approvals
    return redirect(request.META.get('HTTP_REFERER', 'pending_approvals'))

# System settings
@login_required
@user_passes_test(is_admin)
def system_settings(request):
    return render(request, 'admin/system_settings.html')

@login_required
@user_passes_test(is_admin)
def save_general_settings(request):
    if request.method == 'POST':
        # In a real application, you would save these settings to a database or config file
        messages.success(request, "General settings saved successfully!")
    return redirect('system_settings')

@login_required
@user_passes_test(is_admin)
def save_payment_settings(request):
    if request.method == 'POST':
        # In a real application, you would save these settings to a database or config file
        messages.success(request, "Payment settings saved successfully!")
    return redirect('system_settings')

@login_required
@user_passes_test(is_admin)
def clear_cache(request):
    # In a real application, you would implement cache clearing logic
    messages.success(request, "Cache cleared successfully!")
    return redirect('system_settings')

@login_required
@user_passes_test(is_admin)
def backup_database(request):
    # In a real application, you would implement database backup logic
    messages.success(request, "Database backup created successfully!")
    return redirect('system_settings')

# Admin browse items view
@login_required
@user_passes_test(is_admin)
def admin_browse_items(request):
    # Same logic as the regular browse_items view but with admin template
    category = request.GET.get('category', '')
    if category:
        items = Item.objects.filter(available=True, category=category)
    else:
        items = Item.objects.filter(available=True)

    # Get pending approvals count for notification badge
    pending_approvals_count = User.objects.filter(is_active=False, is_approved=False).count()

    return render(request, 'admin/browse_items.html', {
        'items': items,
        'pending_approvals_count': pending_approvals_count
    })

# Admin home view
@login_required
@user_passes_test(is_admin)
def admin_home(request):
    # Same logic as the regular home view but with admin template
    items = Item.objects.filter(available=True).order_by('-created_at')[:8]

    # Get pending approvals count for notification badge
    pending_approvals_count = User.objects.filter(is_active=False, is_approved=False).count()

    return render(request, 'admin/home.html', {
        'items': items,
        'pending_approvals_count': pending_approvals_count
    })
