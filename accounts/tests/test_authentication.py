#pylint: disable=missing-docstring, invalid-name
from django.test import TestCase
from django.contrib.auth import get_user_model
from accounts.authentication import PasswordlessAuthenticationBackend
from accounts.models import Token
User = get_user_model()


class AuthenticateTest(TestCase):

    def test__authenticate__when_token_does_not_exist__returns_None(self):
        result = PasswordlessAuthenticationBackend().authenticate(
            'no-such-token'
        )

        self.assertIsNone(result)


    def test__authenticate__when_token_exists_and_new_user__returns_the_user(self):
        email = 'edith@example.com'
        token = Token.objects.create(email=email)
        user = PasswordlessAuthenticationBackend().authenticate(token.uid)

        new_user = User.objects.get(email=email)

        self.assertEqual(user, new_user)


    def test_authenticate__when_token_exists_and_existing_user__returns_the_user(self):
        email = 'edith@example.com'
        existing_user = User.objects.create(email=email)
        token = Token.objects.create(email=email)

        user = PasswordlessAuthenticationBackend().authenticate(token.uid)

        self.assertEqual(user, existing_user)


class GetUserTest(TestCase):

    def test__get_user__when_email_matches_user__returns_the_user(self):
        User.objects.create(email='another@example.com')
        desired_user = User.objects.create(email='edith@example.com')

        found_user = PasswordlessAuthenticationBackend().get_user(
            'edith@example.com'
        )

        self.assertEqual(found_user, desired_user)


    def test__get_user__when_email_not_matches_user__returns_None(self):
        self.assertIsNone(
            PasswordlessAuthenticationBackend().get_user('edith@example.com')
        )
