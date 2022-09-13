from structlog import get_logger

from lego import celery_app
from lego.apps.email.notifications import WeeklyNotification
from lego.apps.users.models import AbakusGroup
from lego.utils.tasks import AbakusTask

log = get_logger()


@celery_app.task(serializer="json", bind=True, base=AbakusTask)
def send_weekly_email(self, logger_context=None):
    # Set to just PR and Webkom for testing purposes
    all_users = set(
        AbakusGroup.objects.get(name="Webkom").restricted_lookup()[0]
        + AbakusGroup.objects.get(name="PR").restricted_lookup()[0]
    )

    self.setup_logger(logger_context)

    for user in all_users:
        notification = WeeklyNotification(user)
        notification.notify()
