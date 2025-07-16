from django.contrib import admin
from .models import JobApplication, Reminder, Notification

# Register your models here.

admin.site.register(JobApplication)
admin.site.register(Reminder)
admin.site.register(Notification)
