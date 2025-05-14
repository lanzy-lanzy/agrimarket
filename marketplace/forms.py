from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Item
from django.utils import timezone
from datetime import timedelta

class CustomUserCreationForm(UserCreationForm):
    is_seller = forms.BooleanField(required=False, label='Register as a Seller')
    is_buyer = forms.BooleanField(required=False, label='Register as a Buyer')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'is_seller', 'is_buyer')

    def clean(self):
        cleaned_data = super().clean()
        is_seller = cleaned_data.get('is_seller')
        is_buyer = cleaned_data.get('is_buyer')

        if not is_seller and not is_buyer:
            raise forms.ValidationError('You must select at least one role: Seller or Buyer')

        return cleaned_data

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['name', 'description', 'category', 'price', 'available', 'image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class SalesReportForm(forms.Form):
    REPORT_PERIOD_CHOICES = [
        ('', 'Select Period'),
        ('today', 'Today'),
        ('yesterday', 'Yesterday'),
        ('this_week', 'This Week'),
        ('last_week', 'Last Week'),
        ('this_month', 'This Month'),
        ('last_month', 'Last Month'),
        ('this_year', 'This Year'),
        ('custom', 'Custom Date Range'),
    ]

    CATEGORY_CHOICES = [
        ('', 'All Categories'),
        ('livestock', 'Livestock'),
        ('poultry', 'Poultry'),
    ]

    report_period = forms.ChoiceField(
        choices=REPORT_PERIOD_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select rounded-md border-gray-300'})
    )

    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-input rounded-md border-gray-300'})
    )

    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-input rounded-md border-gray-300'})
    )

    category = forms.ChoiceField(
        choices=CATEGORY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select rounded-md border-gray-300'})
    )

    def clean(self):
        cleaned_data = super().clean()
        report_period = cleaned_data.get('report_period')
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        # If custom date range is selected, both start and end dates are required
        if report_period == 'custom':
            if not start_date:
                self.add_error('start_date', 'Start date is required for custom date range')
            if not end_date:
                self.add_error('end_date', 'End date is required for custom date range')
            if start_date and end_date and start_date > end_date:
                self.add_error('end_date', 'End date must be after start date')

        # Set date range based on selected period
        today = timezone.now().date()

        if report_period == 'today':
            cleaned_data['start_date'] = today
            cleaned_data['end_date'] = today
        elif report_period == 'yesterday':
            yesterday = today - timedelta(days=1)
            cleaned_data['start_date'] = yesterday
            cleaned_data['end_date'] = yesterday
        elif report_period == 'this_week':
            start_of_week = today - timedelta(days=today.weekday())
            cleaned_data['start_date'] = start_of_week
            cleaned_data['end_date'] = today
        elif report_period == 'last_week':
            start_of_last_week = today - timedelta(days=today.weekday() + 7)
            end_of_last_week = start_of_last_week + timedelta(days=6)
            cleaned_data['start_date'] = start_of_last_week
            cleaned_data['end_date'] = end_of_last_week
        elif report_period == 'this_month':
            start_of_month = today.replace(day=1)
            cleaned_data['start_date'] = start_of_month
            cleaned_data['end_date'] = today
        elif report_period == 'last_month':
            last_month = today.replace(day=1) - timedelta(days=1)
            start_of_last_month = last_month.replace(day=1)
            cleaned_data['start_date'] = start_of_last_month
            cleaned_data['end_date'] = last_month
        elif report_period == 'this_year':
            start_of_year = today.replace(month=1, day=1)
            cleaned_data['start_date'] = start_of_year
            cleaned_data['end_date'] = today

        return cleaned_data
