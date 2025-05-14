from django import template
from decimal import Decimal

register = template.Library()

@register.filter(name='currency')
def currency(value):
    """
    Format a number as a currency with ₱ symbol, 2 decimal places, and thousand separators.
    
    Example:
        {{ 1234.5|currency }} will output ₱1,234.50
    """
    if value is None:
        return "₱0.00"
    
    try:
        # Convert to Decimal for consistent handling
        value = Decimal(str(value))
        # Format with thousand separators and 2 decimal places
        formatted_value = '{:,.2f}'.format(value)
        return f"₱{formatted_value}"
    except (ValueError, TypeError):
        return "₱0.00"

@register.filter(name='currency_no_symbol')
def currency_no_symbol(value):
    """
    Format a number as a currency with 2 decimal places and thousand separators, but no ₱ symbol.
    
    Example:
        {{ 1234.5|currency_no_symbol }} will output 1,234.50
    """
    if value is None:
        return "0.00"
    
    try:
        # Convert to Decimal for consistent handling
        value = Decimal(str(value))
        # Format with thousand separators and 2 decimal places
        return '{:,.2f}'.format(value)
    except (ValueError, TypeError):
        return "0.00"
