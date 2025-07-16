from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import JobApplication
from .forms import JobApplicationForm
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.db import models
from django.views.decorators.http import require_GET
from .forms import ReminderForm
from .models import Reminder
from .forms import ProfileForm, UserForm
from .models import Profile
from django.utils import timezone
from collections import OrderedDict
import calendar
import datetime
from collections import Counter
from django.contrib.auth.forms import PasswordChangeForm
from .forms import PreferencesForm, TwoFactorAuthForm, APIKeyForm, APIKeyRevokeForm
from .models import UserPreferences, TwoFactorAuth, APIKey
import base64
import secrets
try:
    import pyotp
except ImportError:
    pyotp = None

# Create your views here.

@login_required
def dashboard(request):
    applications = JobApplication.objects.filter(user=request.user)
    search_query = request.GET.get('search', '').strip()
    status_filter = request.GET.get('status', '').strip()
    if search_query:
        applications = applications.filter(
            models.Q(company__icontains=search_query) |
            models.Q(position__icontains=search_query)
        )
    if status_filter:
        applications = applications.filter(status=status_filter)
    status_counts = {
        'applied': applications.filter(status='applied').count(),
        'interview': applications.filter(status='interview').count(),
        'offer': applications.filter(status='offer').count(),
        'rejected': applications.filter(status='rejected').count(),
        'accepted': applications.filter(status='accepted').count(),
        'total': applications.count(),
    }
    unread_reminders_count = Reminder.objects.filter(user=request.user, remind_at__gte=timezone.now(), sent=False).count()
    return render(request, 'tracker/dashboard.html', {
        'applications': applications,
        'status_counts': status_counts,
        'search_query': search_query,
        'status_filter': status_filter,
        'unread_reminders_count': unread_reminders_count,
    })

@login_required
def applications_list(request):
    applications = JobApplication.objects.filter(user=request.user)
    search_query = request.GET.get('search', '').strip()
    status_filter = request.GET.get('status', '').strip()
    if search_query:
        applications = applications.filter(
            models.Q(company__icontains=search_query) |
            models.Q(position__icontains=search_query)
        )
    if status_filter:
        applications = applications.filter(status=status_filter)
    status_counts = {
        'applied': applications.filter(status='applied').count(),
        'interview': applications.filter(status='interview').count(),
        'offer': applications.filter(status='offer').count(),
        'rejected': applications.filter(status='rejected').count(),
        'accepted': applications.filter(status='accepted').count(),
        'total': applications.count(),
    }
    return render(request, 'tracker/applications_list.html', {
        'applications': applications,
        'status_counts': status_counts,
        'search_query': search_query,
        'status_filter': status_filter,
    })

@login_required
def application_create(request):
    if request.method == 'POST':
        form = JobApplicationForm(request.POST)
        if form.is_valid():
            app = form.save(commit=False)
            app.user = request.user
            app.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            return redirect('dashboard')
    else:
        form = JobApplicationForm()
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('tracker/application_form_modal.html', {'form': form, 'action': 'Add'})
        return JsonResponse({'success': False, 'html': html})
    return render(request, 'tracker/application_form.html', {'form': form})

@login_required
def application_update(request, pk):
    app = get_object_or_404(JobApplication, pk=pk, user=request.user)
    if request.method == 'POST':
        form = JobApplicationForm(request.POST, instance=app)
        if form.is_valid():
            form.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            return redirect('dashboard')
    else:
        form = JobApplicationForm(instance=app)
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('tracker/application_form_modal.html', {'form': form, 'action': 'Edit'})
        return JsonResponse({'success': False, 'html': html})
    return render(request, 'tracker/application_form.html', {'form': form})

@login_required
def application_delete(request, pk):
    app = get_object_or_404(JobApplication, pk=pk, user=request.user)
    if request.method == 'POST':
        app.delete()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        return redirect('dashboard')
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('tracker/application_confirm_delete_modal.html', {'application': app})
        return JsonResponse({'success': False, 'html': html})
    return render(request, 'tracker/application_confirm_delete.html', {'application': app})

@require_GET
@login_required
def notifications_api(request):
    notifications = request.user.notifications.filter(is_read=False).order_by('-created_at')[:10]
    data = [
        {
            'id': n.id,
            'message': n.message,
            'created_at': n.created_at.strftime('%Y-%m-%d %H:%M'),
        }
        for n in notifications
    ]
    return JsonResponse({'notifications': data, 'unread_count': notifications.count()})

@login_required
def reminders_list(request):
    reminders = Reminder.objects.filter(user=request.user).order_by('remind_at')
    return render(request, 'tracker/reminders_list.html', {'reminders': reminders})

@login_required
def reminder_create(request):
    if request.method == 'POST':
        form = ReminderForm(request.POST)
        if form.is_valid():
            reminder = form.save(commit=False)
            reminder.user = request.user
            reminder.save()
            return redirect('reminders_list')
    else:
        form = ReminderForm()
    return render(request, 'tracker/reminder_form.html', {'form': form})

@login_required
def reminder_edit(request, pk):
    reminder = get_object_or_404(Reminder, pk=pk, user=request.user)
    if request.method == 'POST':
        form = ReminderForm(request.POST, instance=reminder)
        if form.is_valid():
            form.save()
            return redirect('reminders_list')
    else:
        form = ReminderForm(instance=reminder)
    return render(request, 'tracker/reminder_form.html', {'form': form})

@login_required
def reminder_delete(request, pk):
    reminder = get_object_or_404(Reminder, pk=pk, user=request.user)
    if request.method == 'POST':
        reminder.delete()
        return redirect('reminders_list')
    return render(request, 'tracker/reminder_confirm_delete.html', {'reminder': reminder})

@login_required
def reports(request):
    applications = JobApplication.objects.filter(user=request.user)
    # Status counts
    status_counts = {
        'applied': applications.filter(status='applied').count(),
        'interview': applications.filter(status='interview').count(),
        'offer': applications.filter(status='offer').count(),
        'rejected': applications.filter(status='rejected').count(),
        'accepted': applications.filter(status='accepted').count(),
        'total': applications.count(),
    }
    # Applications per month (last 12 months)
    now = timezone.now()
    months = [(now - datetime.timedelta(days=30*i)).strftime('%b %Y') for i in range(11, -1, -1)]
    months.reverse()
    monthly_counts = OrderedDict((m, 0) for m in months)
    for app in applications:
        m = app.date_applied.strftime('%b %Y')
        if m in monthly_counts:
            monthly_counts[m] += 1
    monthly_labels = list(monthly_counts.keys())
    monthly_data = list(monthly_counts.values())
    # Top companies
    company_counter = Counter(applications.values_list('company', flat=True))
    top_companies = company_counter.most_common(5)
    return render(request, 'tracker/reports.html', {
        'status_counts': status_counts,
        'monthly_counts': list(monthly_counts.items()),
        'monthly_labels': monthly_labels,
        'monthly_data': monthly_data,
        'top_companies': top_companies,
    })

@login_required
def profile(request):
    user = request.user
    profile = user.profile
    if request.method == 'POST':
        uform = UserForm(request.POST, instance=user)
        pform = ProfileForm(request.POST, request.FILES, instance=profile)
        if uform.is_valid() and pform.is_valid():
            uform.save()
            pform.save()
            return redirect('profile')
    else:
        uform = UserForm(instance=user)
        pform = ProfileForm(instance=profile)
    return render(request, 'tracker/profile.html', {'uform': uform, 'pform': pform, 'profile': profile})

@login_required
def settings_view(request):
    user = request.user
    account_success = None
    password_success = None
    account_error = None
    password_error = None
    preferences_success = None
    preferences_error = None
    twofa_success = None
    twofa_error = None
    apikey_success = None
    apikey_error = None

    # Get or create user preferences
    preferences, _ = UserPreferences.objects.get_or_create(user=user)
    # Get or create 2FA
    twofa, _ = TwoFactorAuth.objects.get_or_create(user=user)
    show_2fa_setup = False
    qr_code_url = None

    apikeys = APIKey.objects.filter(user=user).order_by('-created_at')
    apikey_form = APIKeyForm()
    apikey_revoke_form = APIKeyRevokeForm()

    if request.method == 'POST':
        if 'account_form' in request.POST:
            user_form = UserForm(request.POST, instance=user)
            if user_form.is_valid():
                user_form.save()
                account_success = 'Account updated successfully.'
            else:
                account_error = 'Please correct the errors below.'
            password_form = PasswordChangeForm(user)
            preferences_form = PreferencesForm(initial={
                'theme': preferences.theme,
                'notifications_enabled': preferences.notifications_enabled,
                'language': preferences.language,
                'timezone': preferences.timezone,
            })
        elif 'password_form' in request.POST:
            user_form = UserForm(instance=user)
            password_form = PasswordChangeForm(user, request.POST)
            if password_form.is_valid():
                password_form.save()
                password_success = 'Password changed successfully.'
            else:
                password_error = 'Please correct the errors below.'
            preferences_form = PreferencesForm(initial={
                'theme': preferences.theme,
                'notifications_enabled': preferences.notifications_enabled,
                'language': preferences.language,
                'timezone': preferences.timezone,
            })
        elif 'preferences_form' in request.POST:
            user_form = UserForm(instance=user)
            password_form = PasswordChangeForm(user)
            preferences_form = PreferencesForm(request.POST)
            if preferences_form.is_valid():
                data = preferences_form.cleaned_data
                preferences.theme = data.get('theme', preferences.theme)
                preferences.notifications_enabled = data.get('notifications_enabled', preferences.notifications_enabled)
                preferences.language = data.get('language', preferences.language)
                preferences.timezone = data.get('timezone', preferences.timezone)
                preferences.save()
                preferences_success = 'Preferences updated successfully.'
            else:
                preferences_error = 'Please correct the errors below.'
        elif 'twofa_form' in request.POST:
            twofa_form = TwoFactorAuthForm(request.POST)
            if twofa_form.is_valid():
                action = twofa_form.cleaned_data['action']
                code = twofa_form.cleaned_data['code']
                if action == 'enable':
                    if not pyotp:
                        twofa_error = 'pyotp is not installed on the server.'
                    else:
                        # Generate secret and show QR
                        if not twofa.secret:
                            twofa.secret = pyotp.random_base32()
                            twofa.save()
                        show_2fa_setup = True
                        totp = pyotp.TOTP(twofa.secret)
                        qr_code_url = totp.provisioning_uri(name=user.email, issuer_name='ApplyMate')
                elif action == 'verify':
                    if not pyotp:
                        twofa_error = 'pyotp is not installed on the server.'
                    elif not twofa.secret:
                        twofa_error = 'No secret to verify.'
                    else:
                        totp = pyotp.TOTP(twofa.secret)
                        if totp.verify(code):
                            twofa.is_enabled = True
                            twofa.save()
                            twofa_success = 'Two-Factor Authentication enabled!'
                            show_2fa_setup = False
                        else:
                            twofa_error = 'Invalid authentication code.'
                            show_2fa_setup = True
                            qr_code_url = totp.provisioning_uri(name=user.email, issuer_name='ApplyMate')
                elif action == 'disable':
                    twofa.is_enabled = False
                    twofa.secret = ''
                    twofa.save()
                    twofa_success = 'Two-Factor Authentication disabled.'
            else:
                twofa_error = 'Please correct the errors below.'
        elif 'apikey_form' in request.POST:
            apikey_form = APIKeyForm(request.POST)
            if apikey_form.is_valid():
                apikey = apikey_form.save(commit=False)
                apikey.user = user
                apikey.key = secrets.token_urlsafe(32)[:40]
                apikey.save()
                apikey_success = 'API key generated! Please copy and store it securely.'
                apikey_form = APIKeyForm()  # reset form
                apikeys = APIKey.objects.filter(user=user).order_by('-created_at')
            else:
                apikey_error = 'Please correct the errors below.'
        elif 'apikey_revoke_form' in request.POST:
            apikey_revoke_form = APIKeyRevokeForm(request.POST)
            if apikey_revoke_form.is_valid():
                key_id = apikey_revoke_form.cleaned_data['key_id']
                try:
                    apikey = APIKey.objects.get(id=key_id, user=user)
                    apikey.is_active = False
                    apikey.save()
                    apikey_success = 'API key revoked.'
                    apikeys = APIKey.objects.filter(user=user).order_by('-created_at')
                except APIKey.DoesNotExist:
                    apikey_error = 'API key not found.'
            else:
                apikey_error = 'Invalid request.'
        else:
            user_form = UserForm(instance=user)
            password_form = PasswordChangeForm(user)
            preferences_form = PreferencesForm(initial={
                'theme': preferences.theme,
                'notifications_enabled': preferences.notifications_enabled,
                'language': preferences.language,
                'timezone': preferences.timezone,
            })
            twofa_form = TwoFactorAuthForm()
    else:
        user_form = UserForm(instance=user)
        password_form = PasswordChangeForm(user)
        preferences_form = PreferencesForm(initial={
            'theme': preferences.theme,
            'notifications_enabled': preferences.notifications_enabled,
            'language': preferences.language,
            'timezone': preferences.timezone,
        })
        twofa_form = TwoFactorAuthForm()
        apikey_form = APIKeyForm()
        apikey_revoke_form = APIKeyRevokeForm()

    return render(request, 'tracker/settings.html', {
        'user_form': user_form,
        'password_form': password_form,
        'preferences_form': preferences_form,
        'twofa_form': twofa_form,
        'twofa': twofa,
        'show_2fa_setup': show_2fa_setup,
        'qr_code_url': qr_code_url,
        'twofa_success': twofa_success,
        'twofa_error': twofa_error,
        'account_success': account_success,
        'password_success': password_success,
        'account_error': account_error,
        'password_error': password_error,
        'preferences_success': preferences_success,
        'preferences_error': preferences_error,
        'apikeys': apikeys,
        'apikey_form': apikey_form,
        'apikey_revoke_form': apikey_revoke_form,
        'apikey_success': apikey_success,
        'apikey_error': apikey_error,
    })
