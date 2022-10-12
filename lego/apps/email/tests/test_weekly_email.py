from datetime import timedelta
from unittest.mock import patch

from django.utils import timezone

from lego.apps.email.notifications import WeeklyNotification
from lego.apps.events.models import Pool
from lego.apps.joblistings.models import Joblisting
from lego.apps.users.models import User
from lego.utils.test_utils import BaseTestCase


@patch("lego.utils.email.django_send_mail")
class WeeklyEmailTestCase(BaseTestCase):
    fixtures = [
        "test_users.yaml",
        "test_articles.yaml",
        "test_events.yaml",
        "test_companies.yaml",
        "test_abakus_groups.yaml",
        "test_joblistings.yaml",
    ]

    def setUp(self):
        user = User.objects.all().first()
        pool = Pool.objects.get(pk=1)
        pool.activation_date = timezone.now() + timedelta(days=1)
        pool.save()
        joblisting = Joblisting.objects.first()
        joblisting.created_at = timezone.now() - timedelta(days=1)
        joblisting.save()
        self.notifier = WeeklyNotification(user)

    def assertEmailContains(self, send_mail_mock, content):
        self.notifier.generate_mail()
        email_args = send_mail_mock.call_args[1]
        self.assertIn(content, email_args["html_message"])

    def assertEmailDoesNotContain(self, send_mail_mock, content):
        self.notifier.generate_mail()
        email_args = send_mail_mock.call_args[1]
        self.assertNotIn(content, email_args["html_message"])

    def test_generate_weekly(self, send_mail_mock):
        weekly_text = "Klikk deg inn for å lese"
        self.assertEmailContains(send_mail_mock, weekly_text)

    def test_generate_events(self, send_mail_mock):
        event_title = "Arrangementer med påmelding neste uke"
        self.assertEmailContains(send_mail_mock, event_title)
        self.assertEmailContains(send_mail_mock, "Bedriftspresentasjon")

    def test_generate_joblistings(self, send_mail_mock):
        joblisting_title = "Nye jobbannonser"
        self.assertEmailContains(send_mail_mock, joblisting_title)
        self.assertEmailContains(send_mail_mock, "BEKK")


@patch("lego.utils.email.django_send_mail")
class WeeklyEmailTestCaseNoWeekly(WeeklyEmailTestCase):
    fixtures = [
        "test_users.yaml",
        "test_events.yaml",
        "test_companies.yaml",
        "test_abakus_groups.yaml",
        "test_joblistings.yaml",
    ]

    def test_generate_weekly(self, send_mail_mock):
        weekly_text = "Klikk deg inn for å lese"
        self.assertEmailDoesNotContain(send_mail_mock, weekly_text)

    def test_generate_events(self, send_mail_mock):
        event_title = "Arrangementer med påmelding neste uke"
        self.assertEmailContains(send_mail_mock, event_title)
        self.assertEmailContains(send_mail_mock, "Bedriftspresentasjon")

    def test_generate_joblistings(self, send_mail_mock):
        joblisting_title = "Nye jobbannonser"
        self.assertEmailContains(send_mail_mock, joblisting_title)
        self.assertEmailContains(send_mail_mock, "BEKK")


@patch("lego.utils.email.django_send_mail")
class WeeklyEmailTestCaseNoEventsOrWeekly(WeeklyEmailTestCase):
    fixtures = [
        "test_users.yaml",
        "test_abakus_groups.yaml",
        "test_companies.yaml",
        "test_joblistings.yaml",
    ]

    def setUp(self):
        user = User.objects.all().first()
        self.notifier = WeeklyNotification(user)

    def test_generate_weekly(self, send_mail_mock):
        weekly_text = "Klikk deg inn for å lese"
        self.assertEmailDoesNotContain(send_mail_mock, weekly_text)

    def test_generate_events(self, send_mail_mock):
        event_title = "Arrangementer med påmelding neste uke"
        self.assertEmailDoesNotContain(send_mail_mock, event_title)
        self.assertEmailDoesNotContain(send_mail_mock, "Bedriftspresentasjon")

    def test_generate_joblistings(self, send_mail_mock):
        joblisting_title = "Nye jobbannonser"
        self.assertEmailContains(send_mail_mock, joblisting_title)
        self.assertEmailContains(send_mail_mock, "BEKK")


@patch("lego.utils.email.django_send_mail")
class WeeklyEmailTestCaseNothing(WeeklyEmailTestCase):
    fixtures = [
        "test_users.yaml",
        "test_abakus_groups.yaml",
    ]

    def setUp(self):
        user = User.objects.all().first()
        self.notifier = WeeklyNotification(user)

    def test_generate_weekly(self, send_mail_mock):
        self.assertTrue(send_mail_mock.call_args is None)

    def test_generate_events(self, send_mail_mock):
        self.assertTrue(send_mail_mock.call_args is None)

    def test_generate_joblistings(self, send_mail_mock):
        self.assertTrue(send_mail_mock.call_args is None)
