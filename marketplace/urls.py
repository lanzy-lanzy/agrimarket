from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Home and authentication
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),
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

    # Buyer URLs
    path('buyer/dashboard/', views.buyer_dashboard, name='buyer_dashboard'),
    path('items/', views.browse_items, name='browse_items'),
    path('items/<int:item_id>/', views.item_detail, name='item_detail'),
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/add/<int:item_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('checkout/', views.checkout, name='checkout'),
]
