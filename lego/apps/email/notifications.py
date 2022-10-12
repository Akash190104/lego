from datetime import timedelta

from django.utils import timezone

from lego.apps.events.models import Event
from lego.apps.joblistings.models import Joblisting
from lego.apps.notifications.constants import WEEKLY_MAIL
from lego.apps.notifications.notification import Notification
from lego.apps.permissions.constants import VIEW
from lego.apps.tags.models import Tag

JOB_TYPE_MAPPINGS = {
    "summer_job": "Sommerjobb",
    "part_time": "Deltid",
    "full_time": "Fulltid",
    "master_thesis": "Masteroppgave",
    "other": "Annet",
}

EVENT_TYPE_MAPPINGS = {
    "company_presentation": "Bedriftspresentasjon",
    "lunch_presentation": "Lunchpresentasjon",
    "alternative_presentation": "Alternativ presentasjon",
    "course": "Kurs",
    "breakfast_talk": "Frokostforedrag",
    "kid_event": "KID-arrangement",
    "party": "Fest",
    "social": "Sosialt",
    "other": "Annet",
    "event": "Arrangement",
}


class WeeklyNotification(Notification):

    name = WEEKLY_MAIL

    def generate_mail(self):
        yesterday_timestamp = timezone.now() - timedelta(days=1)
        last_sunday_timestamp = timezone.now() - timedelta(days=7)

        weekly_tag = Tag.objects.filter(tag="weekly").first()
        # Check if weekly tag exists so it does not crash if some idiot deletes the weekly tag
        todays_weekly = (
            weekly_tag.article_set.filter(created_at__gt=yesterday_timestamp).first()
            if weekly_tag
            else None
        )

        week_number = timezone.now().isocalendar().week

        events_next_week = Event.objects.filter(
            pools__activation_date__gt=timezone.now(),
            pools__activation_date__lt=timezone.now() + timedelta(days=7),
        ).distinct()

        filtered_events = filter(
            lambda event: self.user.has_perm(VIEW, obj=event), events_next_week
        )

        filtered_events = filter(
            lambda event: event.get_possible_pools(self.user, True)
            or event.is_admitted(self.user),
            filtered_events,
        )

        joblistings_last_week = Joblisting.objects.filter(
            created_at__gt=last_sunday_timestamp, visible_from__lt=timezone.now()
        )

        joblistings = []
        for joblisting in joblistings_last_week:
            joblistings.append(
                {
                    "id": joblisting.id,
                    "company_name": joblisting.company.name,
                    "type": JOB_TYPE_MAPPINGS[joblisting.job_type],
                    "title": joblisting.title,
                }
            )

        events = []
        for event in filtered_events:
            pools = []
            print(event.title)
            for pool in event.pools.all():
                pools.append(
                    {
                        "name": pool.name,
                        "activation_date": pool.activation_date.strftime(
                            "%d/%m kl. %H:%M"
                        ),
                    }
                )

            events.append(
                {
                    "title": event.title,
                    "id": event.id,
                    "pools": pools,
                    "start_time": event.start_time.strftime("%d/%m kl %H:%M"),
                    "url": event.get_absolute_url(),
                    "type": EVENT_TYPE_MAPPINGS[event.event_type],
                }
            )

        if events or joblistings or todays_weekly:
            return self._delay_mail(
                to_email=self.user.email,
                subject=f"Ukesmail uke {week_number}",
                html_template="email/email/weekly_mail.html",
                plain_template="email/email/weekly_mail.txt",
                context={
                    "events": events,
                    "todays_weekly": ""
                    if todays_weekly is None
                    else todays_weekly.get_absolute_url(),
                    "joblistings": joblistings,
                },
            )
        return
