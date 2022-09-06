from datetime import timedelta

from django.utils import timezone

from lego.apps.events.models import Event
from lego.apps.notifications.constants import WEEKLY_MAIL
from lego.apps.notifications.notification import Notification


class WeeklyNotification(Notification):

    name = WEEKLY_MAIL

    def generate_mail(self):
        week_number = timezone.now().isocalendar().week
        events_next_week = Event.objects.filter(
            start_time__gt=timezone.now(),
            end_time__lt=timezone.now() + timedelta(days=7),
        ).all()
        return self._delay_mail(
            to_email=self.user.email,
            subject="Ukesmail",
            html_template="email/email/weekly_mail.html",
            plain_template="email/email/weekly_mail.txt",
            context={"week_number": week_number, "events_next_week": events_next_week},
        )

    def generate_push(self):
        return self._delay_push(template="email/email/weekly_mail.txt", context={})
