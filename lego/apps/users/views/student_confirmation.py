from rest_framework import status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from structlog import get_logger

from lego.apps.users import constants
from lego.apps.users.models import AbakusGroup
from lego.apps.users.registrations import Registrations
from lego.apps.users.serializers.student_confirmation import (
    StudentConfirmationSerializer,
)
from lego.apps.users.serializers.users import MeSerializer
from lego.utils.tasks import send_email

log = get_logger()


class StudentConfirmationRequestViewSet(viewsets.GenericViewSet):

    serializer_class = StudentConfirmationSerializer
    permission_classes = (IsAuthenticated,)

    def list(self, request):
        """
        Validates a student confirmation token.

        The request errors out if the token has expired or is invalid.
        Request URL: GET /api/v1/users/student-confirmation/?token=<token>
        """
        token = request.GET.get("token")
        if not token:
            raise ValidationError(detail="Student confirmation token is required.")
        student_confirmation = Registrations.validate_student_confirmation_token(token)
        if student_confirmation is None:
            raise ValidationError(detail="Token expired or invalid.")
        return Response(student_confirmation, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        """
        Attempts to create a student confirmation token and email it to the user.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user

        if user.is_verified_student():
            raise ValidationError(detail="Already confirmed a student username")

        student_username = serializer.validated_data.get("student_username")

        token = Registrations.generate_student_confirmation_token(
            student_username,
            serializer.validated_data.get("course"),
            serializer.validated_data.get("member"),
            serializer.validated_data.get("is_two_years"),
        )

        send_email.delay(
            to_email=f"{student_username}@{constants.STUDENT_EMAIL_DOMAIN}",
            context={"token": token, "full_name": user.get_full_name()},
            subject="Verifiser studentstatusen din på Abakus.no",
            plain_template="users/email/student_confirmation.txt",
            html_template="users/email/student_confirmation.html",
            from_email=None,
        )

        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_queryset(self):
        pass


class StudentConfirmationPerformViewSet(viewsets.GenericViewSet):

    serializer_class = StudentConfirmationSerializer
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        """
        Attempts to confirm the student based on the student confirmation token.
        """
        token = request.GET.get("token")
        if not token:
            raise ValidationError(detail="Student confirmation token is required.")

        student_confirmation = Registrations.validate_student_confirmation_token(token)

        if student_confirmation is None:
            raise ValidationError(detail="Token expired or invalid.")

        user = request.user

        if user.is_verified_student():
            raise ValidationError(detail="Already confirmed a student username")

        user.student_username = student_confirmation["student_username"]
        course = student_confirmation["course"].lower()
        is_two_years = student_confirmation["is_two_years"]

        if not user.has_grade_group:
            if course == constants.DATA:
                if is_two_years:
                    grade_group = AbakusGroup.objects.get(
                        name=constants.FOURTH_GRADE_DATA
                    )
                    grade_group.add_user(user)
                else:
                    grade_group = AbakusGroup.objects.get(
                        name=constants.FIRST_GRADE_DATA
                    )
                    grade_group.add_user(user)
            else:
                if is_two_years:
                    grade_group = AbakusGroup.objects.get(
                        name=constants.FOURTH_GRADE_KOMTEK
                    )
                    grade_group.add_user(user)
                else:
                    grade_group = AbakusGroup.objects.get(
                        name=constants.FIRST_GRADE_KOMTEK
                    )
                    grade_group.add_user(user)

        if student_confirmation["member"]:
            member_group = AbakusGroup.objects.get(name=constants.MEMBER_GROUP)
            member_group.add_user(user)

        user.save()

        return Response(MeSerializer(user).data, status=status.HTTP_200_OK)
