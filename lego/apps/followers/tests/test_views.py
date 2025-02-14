from rest_framework import status

from lego.apps.followers.models import FollowCompany, FollowEvent, FollowUser
from lego.apps.users.models import User
from lego.utils.test_utils import BaseAPITestCase


class FollowEventViewTestCase(BaseAPITestCase):

    fixtures = [
        "test_abakus_groups.yaml",
        "test_users.yaml",
        "test_companies.yaml",
        "test_events.yaml",
        "test_followevent.yaml",
    ]
    url = "/api/v1/followers-event/"

    def setUp(self):
        self.user = User.objects.get(id=1)

    def test_list(self):
        """Try to list the follower apis with and without auth."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.force_authenticate(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create(self):
        """Try to follow an event, we should always store the follower as request.user"""
        response = self.client.post(self.url, {"target": 1})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.force_authenticate(self.user)
        response = self.client.post(self.url, {"target": 1})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Always use request.user to set the follower
        response = self.client.post(self.url, {"target": 2, "follower": 2})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        result_id = response.json()["id"]
        self.assertEqual(FollowEvent.objects.get(id=result_id).follower, self.user)

    def test_delete(self):
        """Try to delete follow items"""
        response = self.client.delete(f"{self.url}1/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        denied_user = User.objects.get(id=2)
        self.client.force_authenticate(denied_user)
        response = self.client.delete(f"{self.url}1/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.client.force_authenticate(self.user)
        response = self.client.delete(f"{self.url}1/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class FollowUserViewTestCase(BaseAPITestCase):

    fixtures = ["test_abakus_groups.yaml", "test_users.yaml", "test_followuser.yaml"]
    url = "/api/v1/followers-user/"

    def setUp(self):
        self.user = User.objects.get(id=1)

    def test_list(self):
        """Try to list the follower apis with and without auth."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.force_authenticate(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create(self):
        """Try to follow a user, we should always store the follower as request.user"""
        response = self.client.post(self.url, {"target": 1})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.force_authenticate(self.user)
        response = self.client.post(self.url, {"target": 1})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Always use request.user to set the follower
        response = self.client.post(self.url, {"target": 2, "follower": 2})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        result_id = response.json()["id"]
        self.assertEqual(FollowUser.objects.get(id=result_id).follower, self.user)

    def test_delete(self):
        """Try to delete follow items"""
        response = self.client.delete(f"{self.url}1/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        denied_user = User.objects.get(id=2)
        self.client.force_authenticate(denied_user)
        response = self.client.delete(f"{self.url}1/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.client.force_authenticate(self.user)
        response = self.client.delete(f"{self.url}1/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class FollowCompanyViewTestCase(BaseAPITestCase):

    fixtures = [
        "test_abakus_groups.yaml",
        "test_users.yaml",
        "test_companies.yaml",
        "test_followcompany.yaml",
    ]
    url = "/api/v1/followers-company/"

    def setUp(self):
        self.user = User.objects.get(id=1)

    def test_list(self):
        """Try to list the follower apis with and without auth."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.force_authenticate(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create(self):
        """Try to follow a user, we should always store the follower as request.user"""
        response = self.client.post(self.url, {"target": 1})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.force_authenticate(self.user)
        response = self.client.post(self.url, {"target": 1})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Always use request.user to set the follower
        response = self.client.post(self.url, {"target": 2, "follower": 2})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        result_id = response.json()["id"]
        self.assertEqual(FollowCompany.objects.get(id=result_id).follower, self.user)

    def test_delete(self):
        """Try to delete follow items"""
        response = self.client.delete(f"{self.url}1/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        denied_user = User.objects.get(id=2)
        self.client.force_authenticate(denied_user)
        response = self.client.delete(f"{self.url}1/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.client.force_authenticate(self.user)
        response = self.client.delete(f"{self.url}1/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
