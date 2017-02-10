from datetime import timedelta
from unittest import mock

from django.core.urlresolvers import reverse
from rest_framework.test import APITestCase

from lego.apps.events.models import Event
from lego.apps.users.models import AbakusGroup, Penalty, User
from lego.apps.users.serializers.users import DetailedUserSerializer
from lego.utils.test_utils import fake_time

_test_user_data = {
    'username': 'new_testuser',
    'first_name': 'new',
    'last_name': 'test_user',
    'email': 'new@testuser.com',
}


def _get_list_url():
    return reverse('api:v1:user-list')


def _get_detail_url(username):
    return reverse('api:v1:user-detail', kwargs={'username': username})


def get_test_user():
    user = User(**_test_user_data)
    user.save()

    return user


class ListUsersAPITestCase(APITestCase):
    fixtures = ['test_abakus_groups.yaml', 'test_users.yaml']

    def setUp(self):
        self.all_users = User.objects.all()
        self.with_permission = self.all_users.get(username='useradmin_test')
        self.useradmin_test_group = AbakusGroup.objects.get(name='UserAdminTest')
        self.useradmin_test_group.add_user(self.with_permission)
        self.without_permission = self.all_users.exclude(pk=self.with_permission.pk).first()

    def successful_list(self, user):
        self.client.force_authenticate(user=user)
        response = self.client.get(_get_list_url())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), len(self.all_users))

    def test_without_auth(self):
        response = self.client.get(_get_list_url())
        self.assertEqual(response.status_code, 401)

    def test_with_normal_user(self):
        self.client.force_authenticate(user=self.without_permission)
        response = self.client.get(_get_list_url())

        self.assertEqual(response.status_code, 403)

    def test_with_useradmin(self):
        self.successful_list(self.with_permission)

    def test_with_super_user(self):
        self.successful_list(self.with_permission)


class RetrieveUsersAPITestCase(APITestCase):
    fixtures = ['test_abakus_groups.yaml', 'test_users.yaml']

    def setUp(self):
        self.all_users = User.objects.all()

        self.with_perm = self.all_users.get(username='useradmin_test')
        self.useradmin_test_group = AbakusGroup.objects.get(name='UserAdminTest')
        self.useradmin_test_group.add_user(self.with_perm)
        self.without_perm = self.all_users.exclude(pk=self.with_perm.pk).first()

        self.test_user = get_test_user()

    def successful_retrieve(self, user):
        self.client.force_authenticate(user=user)
        response = self.client.get(_get_detail_url(self.test_user.username))
        self.assertEqual(response.status_code, 200)

    def test_without_auth(self):
        response = self.client.get(_get_detail_url(self.all_users.first().username))
        self.assertEqual(response.status_code, 401)

    def test_with_normal_user(self):
        self.client.force_authenticate(user=self.without_perm)
        response = self.client.get(_get_detail_url(self.test_user.username))
        self.assertEqual(response.status_code, 200)

    def test_self_with_normal_user(self):
        self.client.force_authenticate(user=self.without_perm)
        response = self.client.get(_get_detail_url(self.without_perm.username))
        self.assertEqual(response.status_code, 200)

    def test_with_useradmin(self):
        self.successful_retrieve(self.with_perm)


class CreateUsersAPITestCase(APITestCase):
    fixtures = ['test_abakus_groups.yaml', 'test_users.yaml']

    def setUp(self):
        self.all_users = User.objects.all()

        self.with_perm = self.all_users.get(username='useradmin_test')
        self.useradmin_test_group = AbakusGroup.objects.get(name='UserAdminTest')
        self.useradmin_test_group.add_user(self.with_perm)
        self.without_perm = self.all_users.exclude(pk=self.with_perm.pk).first()

    def successful_create(self, user):
        self.client.force_authenticate(user=user)
        response = self.client.post(_get_list_url(), _test_user_data)

        self.assertEqual(response.status_code, 201)
        created_user = User.objects.get(username=_test_user_data['username'])

        for key, value in _test_user_data.items():
            self.assertEqual(getattr(created_user, key), value)

    def test_with_normal_user(self):
        self.client.force_authenticate(user=self.without_perm)
        response = self.client.post(_get_list_url(), _test_user_data)

        self.assertEqual(response.status_code, 403)

    def test_with_useradmin(self):
        self.successful_create(self.with_perm)

    def test_with_super_user(self):
        self.successful_create(self.with_perm)

    def test_taken_username(self):
        get_test_user()
        self.client.force_authenticate(user=self.with_perm)
        response = self.client.post(_get_list_url(), _test_user_data)

        self.assertEqual(response.status_code, 400)


class UpdateUsersAPITestCase(APITestCase):
    fixtures = ['test_abakus_groups.yaml', 'test_users.yaml']

    modified_user = {
        'username': 'modified_user',
        'first_name': 'modified',
        'last_name': 'user',
        'email': 'modified@testuser.com',
    }

    def setUp(self):
        self.all_users = User.objects.all()

        self.with_perm = self.all_users.get(username='useradmin_test')
        self.useradmin_test_group = AbakusGroup.objects.get(name='UserAdminTest')
        self.useradmin_test_group.add_user(self.with_perm)
        self.without_perm = self.all_users.exclude(pk=self.with_perm.pk).first()

        self.test_user = get_test_user()

    def successful_update(self, updater, update_object):
        self.client.force_authenticate(user=updater)
        response = self.client.put(_get_detail_url(update_object.username), self.modified_user)
        user = User.objects.get(pk=update_object.pk)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(set(response.data.keys()), set(DetailedUserSerializer.Meta.fields))

        for key, value in self.modified_user.items():
            self.assertEqual(getattr(user, key), value)

    def test_self(self):
        self.successful_update(self.without_perm, self.without_perm)

    def test_with_useradmin(self):
        self.successful_update(self.with_perm, self.test_user)

    def test_other_with_normal_user(self):
        self.client.force_authenticate(user=self.without_perm)
        response = self.client.put(_get_detail_url(self.test_user.username), self.modified_user)
        user = User.objects.get(pk=self.test_user.pk)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(user, self.test_user)

    def test_update_with_super_user(self):
        self.successful_update(self.with_perm, self.test_user)


class DeleteUsersAPITestCase(APITestCase):
    fixtures = ['test_abakus_groups.yaml', 'test_users.yaml']

    _test_user_data = {
        'username': 'new_testuser',
        'first_name': 'new',
        'last_name': 'test_user',
        'email': 'new@testuser.com',
    }

    def setUp(self):
        self.all_users = User.objects.all()

        self.with_perm = self.all_users.get(username='useradmin_test')
        self.useradmin_test_group = AbakusGroup.objects.get(name='UserAdminTest')
        self.useradmin_test_group.add_user(self.with_perm)
        self.without_perm = self.all_users.exclude(pk=self.with_perm.pk).first()

        self.test_user = get_test_user()

    def successful_delete(self, user):
        self.client.force_authenticate(user=user)
        response = self.client.delete(_get_detail_url(self.test_user.username))

        self.assertEqual(response.status_code, 204)
        self.assertRaises(User.DoesNotExist, User.objects.get, pk=self.test_user.pk)

    def test_with_normal_user(self):
        self.client.force_authenticate(user=self.without_perm)
        response = self.client.delete(_get_detail_url(self.test_user.username))
        users = User.objects.filter(pk=self.test_user.pk)

        self.assertEqual(response.status_code, 403)
        self.assertTrue(len(users))

    def test_with_useradmin(self):
        self.successful_delete(self.with_perm)


class RetrieveSelfTestCase(APITestCase):
    fixtures = ['initial_abakus_groups.yaml', 'test_users.yaml', 'test_companies.yaml',
                'test_events.yaml']

    def setUp(self):
        self.user = User.objects.get(pk=1)

    def test_self_authed(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('api:v1:user-me'))

        self.assertEqual(response.status_code, 200)
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'full_name',
            'email',
            'is_staff',
            'is_active',
            'penalties'
        )
        for field in fields:
            if field == 'penalties':
                self.assertEqual(len(self.user.penalties.valid()), len(response.data['penalties']))
            else:
                self.assertEqual(getattr(self.user, field), response.data[field])

    def test_self_unauthed(self):
        response = self.client.get(reverse('api:v1:user-me'))
        self.assertEqual(response.status_code, 401)

    @mock.patch('django.utils.timezone.now', return_value=fake_time(2016, 10, 1))
    def test_own_penalties_serializer(self, mock_now):
        source = Event.objects.all().first()
        Penalty.objects.create(created_at=mock_now()-timedelta(days=20),
                               user=self.user, reason='test', weight=1, source_event=source)
        Penalty.objects.create(created_at=mock_now()-timedelta(days=19,
                                                               hours=23,
                                                               minutes=59),
                               user=self.user, reason='test', weight=1, source_event=source)
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('api:v1:user-me'))

        self.assertEqual(response.status_code, 200)

        self.assertEqual(len(self.user.penalties.valid()), len(response.data['penalties']))
        self.assertEqual(len(response.data['penalties']), 1)
        self.assertEqual(len(response.data['penalties'][0]), 5)
