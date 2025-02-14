from lego.apps.notifications import constants
from lego.apps.notifications.models import NotificationSetting
from lego.apps.users.models import User
from lego.utils.test_utils import BaseTestCase


class NotificationSettingTestCase(BaseTestCase):

    fixtures = [
        "test_abakus_groups.yaml",
        "test_users.yaml",
        "test_notification_settings.yaml",
    ]

    def test_no_restrictions(self):
        """
        A user with no setting should get a list of all channels when asking for a valid
        notification_type
        """
        user = User.objects.get(pk=1)
        self.assertEqual(
            NotificationSetting.active_channels(user, constants.WEEKLY_MAIL),
            constants.CHANNELS,
        )

    def test_invalid_notification_type(self):
        """Invalid notification type should raise a ValueError"""
        user = User.objects.get(pk=1)
        self.assertRaises(
            ValueError, NotificationSetting.active_channels, user, "invalid"
        )

    def test_disabled(self):
        """enabled=False should return an empty list"""
        user2 = User.objects.get(pk=2)
        user3 = User.objects.get(pk=3)

        self.assertEqual(
            NotificationSetting.active_channels(user2, constants.WEEKLY_MAIL), []
        )
        self.assertEqual(
            NotificationSetting.active_channels(user3, constants.WEEKLY_MAIL), []
        )

    def test_enabled(self):
        """enabled=True should return a list with valid channels"""
        user = User.objects.get(pk=4)

        self.assertEqual(
            NotificationSetting.active_channels(user, constants.WEEKLY_MAIL),
            [constants.EMAIL],
        )
