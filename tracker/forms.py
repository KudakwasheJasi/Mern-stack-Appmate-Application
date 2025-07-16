from django import forms
from .models import JobApplication
from .models import Reminder
from .models import Profile
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from .models import APIKey

class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = ['company', 'position', 'date_applied', 'status', 'notes', 'job_link', 'company_logo'] 

class ReminderForm(forms.ModelForm):
    class Meta:
        model = Reminder
        fields = ['job_application', 'remind_at', 'message']
        widgets = {
            'remind_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        } 

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['profile_pic', 'title', 'role', 'phone_number', 'bio']

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email'] 

class PreferencesForm(forms.Form):
    THEME_CHOICES = [
        ('dark', 'Dark'),
        ('light', 'Light'),
        ('system', 'System Default'),
    ]
    theme = forms.ChoiceField(choices=THEME_CHOICES, required=False)
    notifications_enabled = forms.BooleanField(required=False)
    language = forms.ChoiceField(choices=[('en', 'English')], required=False)  # Extend as needed
    timezone = forms.ChoiceField(choices=[('UTC', 'UTC')], required=False)  # Extend as needed 

class TwoFactorAuthForm(forms.Form):
    action = forms.ChoiceField(choices=[('enable', 'Enable'), ('disable', 'Disable'), ('verify', 'Verify')], widget=forms.HiddenInput)
    code = forms.CharField(max_length=6, required=False, label='Authentication Code') 

class APIKeyForm(forms.ModelForm):
    class Meta:
        model = APIKey
        fields = ['name', 'allowed_ips', 'expires_at']
    # key is generated automatically

class APIKeyRevokeForm(forms.Form):
    key_id = forms.IntegerField(widget=forms.HiddenInput) 