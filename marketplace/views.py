from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q, Count
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.contrib.auth.views import LoginView
from .models import User, Item, Cart, CartItem, Payment, Sale
from django.urls import reverse
from .forms import CustomUserCreationForm, SalesReportForm
from django.utils import timezone
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.legends import Legend
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

def home(request):
    items = Item.objects.filter(available=True).order_by('-created_at')[:8]
    return render(request, 'home.html', {'items': items})

# Authentication views
def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user_type = request.POST.get('user_type')
            if user_type == 'seller':
                user.is_seller = True
            else:
                user.is_buyer = True
            user.save()
            login(request, user)
            # Redirect to appropriate dashboard based on user type
            if user.is_seller:
                return redirect('seller_dashboard')
            elif user.is_buyer:
                return redirect('buyer_dashboard')
            else:
                return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

class CustomLoginView(LoginView):
    template_name = 'login.html'

    def get_success_url(self):
        # Redirect to appropriate dashboard based on user type
        user = self.request.user
        if user.is_seller:
            return '/seller/dashboard/'
        elif user.is_buyer:
            return '/buyer/dashboard/'
        else:
            return '/'

# Seller views
@login_required
def seller_dashboard(request):
    if not request.user.is_seller:
        return redirect('home')

    items = Item.objects.filter(seller=request.user)
    sales = Sale.objects.filter(seller=request.user)
    total_sales = sales.aggregate(total=Sum('total_price'))['total'] or 0

    # Get pending payments for this seller's items
    pending_payments_count = Payment.objects.filter(
        status='pending',
        cart__items__item__seller=request.user
    ).distinct().count()

    return render(request, 'seller/dashboard.html', {
        'items': items,
        'sales': sales,
        'total_sales': total_sales,
        'pending_payments_count': pending_payments_count
    })

@login_required
def add_item(request):
    if not request.user.is_seller:
        return redirect('home')

    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        category = request.POST.get('category')
        price = request.POST.get('price')
        image = request.FILES.get('image')

        item = Item.objects.create(
            seller=request.user,
            name=name,
            description=description,
            category=category,
            price=price,
            image=image
        )

        return redirect('seller_dashboard')

    return render(request, 'seller/add_item.html')

@login_required
def edit_item(request, item_id):
    if not request.user.is_seller:
        return redirect('home')

    item = get_object_or_404(Item, id=item_id, seller=request.user)

    if request.method == 'POST':
        item.name = request.POST.get('name')
        item.description = request.POST.get('description')
        item.category = request.POST.get('category')
        item.price = request.POST.get('price')
        if 'image' in request.FILES:
            item.image = request.FILES.get('image')
        item.available = 'available' in request.POST
        item.save()

        return redirect('seller_dashboard')

    return render(request, 'seller/edit_item.html', {'item': item})

@login_required
def pending_payments(request):
    if not request.user.is_seller:
        return redirect('home')

    # Get payments that include items from this seller
    payments = Payment.objects.filter(
        status='pending',
        cart__items__item__seller=request.user
    ).distinct().order_by('-paid_at')

    return render(request, 'seller/pending_payments.html', {
        'payments': payments
    })

@login_required
def payment_detail(request, payment_id):
    if not request.user.is_seller:
        return redirect('home')

    payment = get_object_or_404(Payment, id=payment_id)

    # Check if this seller has items in this payment
    seller_items = payment.get_items_by_seller(request.user)
    if not seller_items.exists():
        messages.error(request, "You don't have any items in this payment")
        return redirect('pending_payments')

    # Calculate total for this seller's items
    seller_total = sum(item.total_price() for item in seller_items)

    return render(request, 'seller/payment_detail.html', {
        'payment': payment,
        'seller_items': seller_items,
        'seller_total': seller_total
    })

@login_required
@require_POST
def approve_payment(request, payment_id):
    if not request.user.is_seller:
        return redirect('home')

    payment = get_object_or_404(Payment, id=payment_id)

    # Check if this seller has items in this payment
    seller_items = payment.get_items_by_seller(request.user)
    if not seller_items.exists():
        messages.error(request, "You don't have any items in this payment")
        return redirect('pending_payments')

    # Create sales records for this seller's items
    for cart_item in seller_items:
        Sale.objects.create(
            item=cart_item.item,
            buyer=payment.buyer,
            seller=request.user,
            payment=payment,
            quantity=cart_item.quantity,
            total_price=cart_item.total_price()
        )

    # Update payment status
    payment.status = 'approved'
    payment.approved_by = request.user
    payment.approved_at = timezone.now()
    payment.verified = True
    payment.save()

    messages.success(request, "Payment approved successfully. Sales records have been created.")
    return redirect('seller_dashboard')

@login_required
def sales_report(request):
    if not request.user.is_seller:
        return redirect('home')

    form = SalesReportForm(request.GET or None)
    context = {'form': form}

    if form.is_valid():
        # Get filter parameters
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')
        category = form.cleaned_data.get('category')

        # Base query for sales
        sales_query = Sale.objects.filter(seller=request.user)

        # Apply date filters
        if start_date:
            sales_query = sales_query.filter(sold_at__date__gte=start_date)
        if end_date:
            # Add one day to include the end date fully
            end_date_next = end_date + timezone.timedelta(days=1)
            sales_query = sales_query.filter(sold_at__date__lt=end_date_next)

        # Apply category filter if selected
        if category:
            sales_query = sales_query.filter(item__category=category)
            context['selected_category'] = category
            context['selected_category_display'] = dict(Item.SELL_CATEGORY).get(category, category)

        # Get sales data
        sales = sales_query.order_by('-sold_at')

        # Calculate totals
        total_revenue = sales.aggregate(total=Sum('total_price'))['total'] or 0
        total_quantity = sales.aggregate(total=Sum('quantity'))['total'] or 0

        # Get sales by category
        category_data = {}
        for cat, cat_display in Item.SELL_CATEGORY:
            cat_sales = sales.filter(item__category=cat)
            if cat_sales.exists():
                cat_revenue = cat_sales.aggregate(total=Sum('total_price'))['total'] or 0
                cat_count = cat_sales.count()
                category_data[cat_display] = {
                    'count': cat_count,
                    'revenue': cat_revenue
                }

        # Add data to context
        context.update({
            'sales': sales,
            'total_revenue': total_revenue,
            'total_quantity': total_quantity,
            'category_data': category_data,
            'start_date': start_date,
            'end_date': end_date
        })

    return render(request, 'seller/sales_report.html', context)

@login_required
def generate_sales_pdf(request):
    if not request.user.is_seller:
        return redirect('home')

    # Process the same filters as in the sales_report view
    form = SalesReportForm(request.GET or None)

    if not form.is_valid():
        return redirect('sales_report')

    # Get filter parameters
    start_date = form.cleaned_data.get('start_date')
    end_date = form.cleaned_data.get('end_date')
    category = form.cleaned_data.get('category')

    # Base query for sales
    sales_query = Sale.objects.filter(seller=request.user)

    # Apply date filters
    if start_date:
        sales_query = sales_query.filter(sold_at__date__gte=start_date)
    if end_date:
        # Add one day to include the end date fully
        end_date_next = end_date + timezone.timedelta(days=1)
        sales_query = sales_query.filter(sold_at__date__lt=end_date_next)

    # Apply category filter if selected
    selected_category_display = None
    if category:
        sales_query = sales_query.filter(item__category=category)
        selected_category_display = dict(Item.SELL_CATEGORY).get(category, category)

    # Get sales data
    sales = sales_query.order_by('-sold_at')

    # Calculate totals
    total_revenue = sales.aggregate(total=Sum('total_price'))['total'] or 0
    total_quantity = sales.aggregate(total=Sum('quantity'))['total'] or 0

    # Get sales by category
    category_data = {}
    for cat, cat_display in Item.SELL_CATEGORY:
        cat_sales = sales.filter(item__category=cat)
        if cat_sales.exists():
            cat_revenue = cat_sales.aggregate(total=Sum('total_price'))['total'] or 0
            cat_count = cat_sales.count()
            category_data[cat_display] = {
                'count': cat_count,
                'revenue': cat_revenue
            }

    # Create the PDF
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()

    # Create custom styles
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=16,
        alignment=TA_CENTER,
        textColor=HexColor('#664343')  # AgriMarket brown-dark
    )

    heading_style = ParagraphStyle(
        'Heading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=HexColor('#795757')  # AgriMarket brown
    )

    normal_style = styles['Normal']

    # Create the content
    content = []

    # Title
    content.append(Paragraph("AgriMarket Sales Report", title_style))
    content.append(Spacer(1, 0.25*inch))

    # Seller info
    content.append(Paragraph(f"Seller: {request.user.username}", normal_style))

    # Date range
    if start_date == end_date:
        date_text = f"Date: {start_date.strftime('%B %d, %Y')}"
    else:
        date_text = f"Period: {start_date.strftime('%B %d, %Y')} to {end_date.strftime('%B %d, %Y')}"
    content.append(Paragraph(date_text, normal_style))

    # Category filter if applied
    if selected_category_display:
        content.append(Paragraph(f"Category: {selected_category_display}", normal_style))

    content.append(Spacer(1, 0.25*inch))

    # Summary section
    content.append(Paragraph("Summary", heading_style))
    content.append(Spacer(1, 0.1*inch))

    summary_data = [
        ["Total Sales", f"{sales.count()}"],
        ["Total Revenue", f"₱{total_revenue:,.2f}"],
        ["Total Items Sold", f"{total_quantity:,}"]
    ]

    summary_table = Table(summary_data, colWidths=[2*inch, 1.5*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), HexColor('#FFF0D1')),  # AgriMarket cream
        ('TEXTCOLOR', (0, 0), (0, -1), HexColor('#3B3030')),  # AgriMarket brown-darker
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#795757')),
    ]))
    content.append(summary_table)
    content.append(Spacer(1, 0.25*inch))

    # Category breakdown if we have multiple categories
    if len(category_data) > 1:
        content.append(Paragraph("Sales by Category", heading_style))
        content.append(Spacer(1, 0.1*inch))

        cat_data = [["Category", "Count", "Revenue"]]
        for cat, data in category_data.items():
            cat_data.append([cat, f"{data['count']:,}", f"₱{data['revenue']:,.2f}"])

        cat_table = Table(cat_data, colWidths=[2*inch, 1*inch, 1.5*inch])
        cat_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#795757')),  # Header row
            ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#FFFFFF')),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#795757')),
        ]))
        content.append(cat_table)
        content.append(Spacer(1, 0.25*inch))

    # Detailed sales table
    content.append(Paragraph("Detailed Sales", heading_style))
    content.append(Spacer(1, 0.1*inch))

    # Table header
    detailed_data = [["Date", "Item", "Category", "Buyer", "Qty", "Price", "Total"]]

    # Table rows
    for sale in sales:
        detailed_data.append([
            sale.sold_at.strftime("%m/%d/%Y"),
            sale.item.name,
            sale.item.get_category_display(),
            sale.buyer.username,
            f"{sale.quantity:,}",
            f"₱{sale.item.price:,.2f}",
            f"₱{sale.total_price:,.2f}"
        ])

    # Add totals row
    detailed_data.append([
        "", "", "", "TOTAL", f"{total_quantity:,}", "", f"₱{total_revenue:,.2f}"
    ])

    # Create and style the table
    detailed_table = Table(detailed_data, repeatRows=1)
    detailed_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#795757')),  # Header row
        ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#FFFFFF')),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('ALIGN', (4, 1), (6, -1), 'RIGHT'),  # Right align numbers
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),  # Bold for totals row
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#795757')),
    ]))
    content.append(detailed_table)

    # Build the PDF
    doc.build(content)

    # Get the value of the BytesIO buffer
    pdf = buffer.getvalue()
    buffer.close()

    # Generate filename
    if start_date == end_date:
        filename = f"sales_report_{start_date.strftime('%Y%m%d')}.pdf"
    else:
        filename = f"sales_report_{start_date.strftime('%Y%m%d')}_to_{end_date.strftime('%Y%m%d')}.pdf"

    # Create the HttpResponse with PDF headers
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    return response

# Buyer views
@login_required
def buyer_dashboard(request):
    if not request.user.is_buyer:
        return redirect('home')

    cart = Cart.get_cart_for_user(request.user)
    payments = Payment.objects.filter(buyer=request.user)

    return render(request, 'buyer/dashboard.html', {
        'cart': cart,
        'payments': payments
    })

def browse_items(request):
    category = request.GET.get('category', '')
    if category:
        items = Item.objects.filter(available=True, category=category)
    else:
        items = Item.objects.filter(available=True)

    return render(request, 'buyer/browse_items.html', {'items': items})

@login_required
def item_detail(request, item_id):
    item = get_object_or_404(Item, id=item_id, available=True)
    return render(request, 'buyer/item_detail.html', {'item': item})

@login_required
@require_POST
def add_to_cart(request, item_id):
    if not request.user.is_buyer:
        return JsonResponse({'error': 'Only buyers can add items to cart'}, status=403)

    item = get_object_or_404(Item, id=item_id, available=True)
    cart = Cart.get_cart_for_user(request.user)

    cart_item, created = CartItem.objects.get_or_create(cart=cart, item=item)
    if not created:
        cart_item.quantity += 1
        cart_item.save()

    response = JsonResponse({
        'success': True,
        'cart_total': cart.total_price(),
        'cart_items': cart.total_quantity()  # Use total_quantity instead of items.count()
    })

    # Add a custom header to trigger cart update
    response['HX-Trigger'] = 'cartUpdated'
    return response

@login_required
def view_cart(request):
    if not request.user.is_buyer:
        return redirect('home')

    cart = Cart.get_cart_for_user(request.user)
    return render(request, 'buyer/cart.html', {'cart': cart})

@login_required
@require_POST
def update_cart_item(request, item_id):
    if not request.user.is_buyer:
        return redirect('home')

    cart = Cart.get_cart_for_user(request.user)
    cart_item = get_object_or_404(CartItem, cart=cart, item_id=item_id)

    action = request.POST.get('action')
    if action == 'increase':
        cart_item.quantity += 1
        cart_item.save()
    elif action == 'decrease':
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    elif action == 'remove':
        cart_item.delete()

    # Redirect back to the cart page instead of returning JSON
    return redirect('view_cart')

@login_required
def checkout(request):
    if not request.user.is_buyer:
        return redirect('home')

    cart = Cart.get_cart_for_user(request.user)
    if not cart or not cart.items.exists():
        messages.error(request, 'Your cart is empty')
        return redirect('view_cart')

    if request.method == 'POST':
        gcash_reference = request.POST.get('gcash_reference')
        proof_screenshot = request.FILES.get('proof_screenshot')

        if not gcash_reference or not proof_screenshot:
            messages.error(request, 'Please provide GCash reference and proof screenshot')
            return redirect('checkout')

        # Create payment record with pending status
        payment = Payment.objects.create(
            cart=cart,
            buyer=request.user,
            gcash_reference=gcash_reference,
            proof_screenshot=proof_screenshot,
            status='pending'
        )

        # Sales records will be created when the payment is approved by the seller

        # Mark the current cart as processed by setting it to inactive
        try:
            cart.available = False
            cart.save()
        except Exception:
            # If the available field doesn't exist yet, just create a new cart
            # This is a fallback and should be removed once migrations are complete
            pass

        # The next time the user visits, a new cart will be created automatically

        messages.success(request, 'Your order has been placed successfully!')
        return redirect('buyer_dashboard')

    return render(request, 'buyer/checkout.html', {'cart': cart})
