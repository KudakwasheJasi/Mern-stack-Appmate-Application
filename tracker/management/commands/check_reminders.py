from django.core.management.base import BaseCommand
from django.utils import timezone
from tracker.models import Reminder, Notification

class Command(BaseCommand):
    help = 'Check for due reminders and create notifications'

    def handle(self, *args, **kwargs):
        now = timezone.now()
        soon = now + timezone.timedelta(hours=1)
        reminders = Reminder.objects.filter(remind_at__lte=soon, remind_at__gte=now, sent=False)
        for reminder in reminders:
            Notification.objects.create(
                user=reminder.user,
                message=f"Reminder: {reminder.message} for {reminder.job_application}",
            )
            reminder.sent = True
            reminder.save()
        self.stdout.write(self.style.SUCCESS('Checked reminders and created notifications.')) 