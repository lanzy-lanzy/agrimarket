from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User, Item
from django.utils import timezone
from datetime import timedelta

class CustomUserCreationForm(UserCreationForm):
    USER_TYPE_CHOICES = [
        ('', 'Select account type'),
        ('buyer', 'Buyer'),
        ('seller', 'Seller'),
    ]

    user_type = forms.ChoiceField(
        choices=USER_TYPE_CHOICES,
        required=True,
        label='Account Type',
        widget=forms.Select(attrs={'class': 'custom-select'})
    )

    # Profile image
    profile_image = forms.ImageField(
        required=False,
        label='Profile Image',
        help_text='Upload a profile picture (optional)'
    )

    # Personal information
    first_name = forms.CharField(max_length=30, required=True, label='First Name')
    last_name = forms.CharField(max_length=30, required=True, label='Last Name')
    email = forms.EmailField(max_length=254, required=True, label='Email Address')

    # Contact information
    phone_number = forms.CharField(max_length=15, required=True, label='Phone Number')
    address = forms.CharField(max_length=255, required=True, label='Address')

    # Terms and conditions
    terms_agreement = forms.BooleanField(
        required=True,
        label='I agree to the Terms and Conditions',
        error_messages={'required': 'You must agree to the terms and conditions to register'}
    )

    # For sellers - additional verification
    business_name = forms.CharField(max_length=100, required=False, label='Business Name (for sellers)')
    business_id = forms.CharField(max_length=50, required=False, label='Business ID/License Number (for sellers)')

    class Meta:
        model = User
        fields = ('username', 'email', 'profile_image', 'first_name', 'last_name', 'phone_number', 'address',
                 'password1', 'password2', 'user_type', 'business_name', 'business_id', 'terms_agreement')

    def clean(self):
        cleaned_data = super().clean()
        user_type = cleaned_data.get('user_type')
        business_name = cleaned_data.get('business_name')
        business_id = cleaned_data.get('business_id')

        if not user_type:
            raise forms.ValidationError('Please select an account type')

        # If registering as a seller, business information is required
        if user_type == 'seller':
            if not business_name:
                self.add_error('business_name', 'Business name is required for sellers')
            if not business_id:
                self.add_error('business_id', 'Business ID/License number is required for sellers')

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user_type = self.cleaned_data.get('user_type')

        # Set is_seller and is_buyer based on user_type selection
        if user_type == 'seller':
            user.is_seller = True
            user.is_buyer = False
        elif user_type == 'buyer':
            user.is_buyer = True
            user.is_seller = False

        if commit:
            user.save()

        return user

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['name', 'description', 'category', 'price', 'available', 'image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class AdminUserCreationForm(UserCreationForm):
    is_superuser = forms.BooleanField(required=False, label='Admin')
    is_seller = forms.BooleanField(required=False, label='Seller')
    is_buyer = forms.BooleanField(required=False, label='Buyer')
    is_active = forms.BooleanField(required=False, initial=True, label='Active')

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

class AdminUserEditForm(UserChangeForm):
    is_superuser = forms.BooleanField(required=False, label='Admin')
    is_seller = forms.BooleanField(required=False, label='Seller')
    is_buyer = forms.BooleanField(required=False, label='Buyer')
    is_active = forms.BooleanField(required=False, label='Active')
    password1 = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput,
        required=False,
        help_text="Leave blank to keep current password."
    )
    password2 = forms.CharField(
        label="Confirm New Password",
        widget=forms.PasswordInput,
        required=False
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')
        exclude = ('password',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove the password field that UserChangeForm adds
        if 'password' in self.fields:
            self.fields.pop('password')

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1:
            if not password2:
                self.add_error('password2', 'You must confirm your password')
            elif password1 != password2:
                self.add_error('password2', 'Your passwords do not match')

        return cleaned_data

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
