from django.core.urlresolvers import reverse
from rest_framework.test import APITestCase

from lego.apps.meetings.models import Meeting
from lego.apps.users.models import User, AbakusGroup


test_meeting_data = [
    {
        'title': 'Halla damer',
        'location': 'Plebkom',
        'start_time': '2016-10-01T13:20:30Z',
        'end_time': '2016-10-01T14:00:30Z',
    }
]


def _get_list_url():
    return reverse('api:v1:meeting-list')


def _get_detail_url(pk):
    return reverse('api:v1:meeting-detail', kwargs={'pk': pk})


class CreateMeetingTestCase(APITestCase):
    fixtures = ['initial_abakus_groups.yaml', 'development_meetings.yaml',
                'test_users.yaml']

    def setUp(self):
        self.abakom_user = User.objects.get(id=1)
        AbakusGroup.objects.get(name='Webkom').add_user(self.abakom_user)

        self.pleb = User.objects.get(username='not_abakommer')
        AbakusGroup.objects.get(name='Abakus').add_user(self.pleb)

    def test_meeting_create(self):
        """
        All Abakom users should be able to create a meeting
        """
        self.client.force_authenticate(user=self.abakom_user)
        res = self.client.post(_get_list_url(), test_meeting_data[0])
        self.assertEqual(res.status_code, 201)

    def test_pleb_cannot_create(self):
        """
        Regular Abakus members cannot create a meeting
        """
        self.client.force_authenticate(self.pleb)
        res = self.client.post(_get_list_url(), test_meeting_data[0])
        self.assertEqual(res.status_code, 403)


class RetrieveMeetingTestCase(APITestCase):
    fixtures = ['initial_abakus_groups.yaml', 'development_meetings.yaml',
                'test_users.yaml']

    def setUp(self):
        self.meeting = Meeting.objects.get(id=1)
        self.abakommer = User.objects.get(username='abakommer')
        AbakusGroup.objects.get(name='Abakom').add_user(self.abakommer)
        self.abakule = User.objects.get(username='test1')
        AbakusGroup.objects.get(name='Abakus').add_user(self.abakule)
        self.pleb = User.objects.get(username='pleb')

    def test_participant_can_retrieve(self):
        invited = self.abakule
        self.client.force_authenticate(invited)
        self.meeting.invite(invited)
        res = self.client.get(_get_detail_url(self.meeting.id))
        self.assertEqual(res.status_code, 200)

    def test_uninvited_cannot_retrieve(self):
        user = self.abakule
        self.client.force_authenticate(user)
        self.meeting.invite(user)
        self.meeting.uninvite(user)
        res = self.client.get(_get_detail_url(self.meeting.pk))
        self.assertTrue(res.status_code >= 403)

    def test_pleb_cannot_retrieve(self):
        self.client.force_authenticate(self.pleb)
        res = self.client.get(_get_detail_url(self.meeting.id))
        self.assertTrue(res.status_code >= 403)

    def test_abakus_can_attend_abameeting(self):
        abameeting = Meeting.objects.get(title='Genvors')
        self.client.force_authenticate(self.abakule)
        res = self.client.get(_get_detail_url(abameeting.id))
        self.assertEqual(res.status_code, 200)
