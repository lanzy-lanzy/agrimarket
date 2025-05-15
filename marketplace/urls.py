from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from . import admin_views

urlpatterns = [
    # Home and authentication
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('registration-pending/', views.registration_pending, name='registration_pending'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home', http_method_names=['get', 'post']), name='logout'),

    # Seller URLs
    path('seller/dashboard/', views.seller_dashboard, name='seller_dashboard'),
    path('seller/add-item/', views.add_item, name='add_item'),
    path('seller/edit-item/<int:item_id>/', views.edit_item, name='edit_item'),
    path('seller/pending-payments/', views.pending_payments, name='pending_payments'),
    path('seller/payment/<int:payment_id>/', views.payment_detail, name='payment_detail'),
    path('seller/payment/<int:payment_id>/approve/', views.approve_payment, name='approve_payment'),
    path('seller/sales-report/', views.sales_report, name='sales_report'),
    path('seller/sales-report/pdf/', views.generate_sales_pdf, name='generate_sales_pdf'),
    path('seller/notification/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),

    # Buyer URLs
    path('buyer/dashboard/', views.buyer_dashboard, name='buyer_dashboard'),
    path('items/', views.browse_items, name='browse_items'),
    path('items/<int:item_id>/', views.item_detail, name='item_detail'),
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/add/<int:item_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('checkout/', views.checkout, name='checkout'),

    # Custom Admin URLs (using custom-admin prefix to avoid conflicts with Django admin)
    path('custom-admin/dashboard/', admin_views.admin_dashboard, name='admin_dashboard'),
    path('custom-admin/browse/', admin_views.admin_browse_items, name='admin_browse_items'),
    path('custom-admin/home/', admin_views.admin_home, name='admin_home'),
    path('custom-admin/users/', admin_views.user_list, name='user_list'),
    path('custom-admin/users/create/', admin_views.user_create, name='user_create'),
    path('custom-admin/users/<int:user_id>/', admin_views.user_detail, name='user_detail'),
    path('custom-admin/users/<int:user_id>/edit/', admin_views.user_edit, name='user_edit'),
    path('custom-admin/users/<int:user_id>/toggle-status/', admin_views.user_toggle_status, name='user_toggle_status'),
    path('custom-admin/pending-approvals/', admin_views.pending_approvals, name='pending_approvals'),
    path('custom-admin/users/<int:user_id>/approve/', admin_views.approve_user, name='approve_user'),
    path('custom-admin/users/<int:user_id>/reject/', admin_views.reject_user, name='reject_user'),
    path('custom-admin/settings/', admin_views.system_settings, name='system_settings'),
    path('custom-admin/settings/general/save/', admin_views.save_general_settings, name='save_general_settings'),
    path('custom-admin/settings/payment/save/', admin_views.save_payment_settings, name='save_payment_settings'),
    path('custom-admin/settings/cache/clear/', admin_views.clear_cache, name='clear_cache'),
    path('custom-admin/settings/database/backup/', admin_views.backup_database, name='backup_database'),

    # Admin Transaction Monitoring URLs
    path('custom-admin/transactions/', admin_views.admin_transactions, name='admin_transactions'),
    path('custom-admin/transactions/<int:payment_id>/', admin_views.admin_transaction_detail, name='admin_transaction_detail'),
    path('custom-admin/transactions/<int:payment_id>/approve/', admin_views.admin_approve_transaction, name='admin_approve_transaction'),
    path('custom-admin/transactions/<int:payment_id>/reject/', admin_views.admin_reject_transaction, name='admin_reject_transaction'),
]
