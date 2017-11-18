#pylint: disable=missing-docstring, invalid-name, line-too-long, attribute-defined-outside-init
from unittest.mock import patch, call
from django.test import TestCase
from accounts.models import Token


class SendLoginEmailViewTest(TestCase):

    def test__send_email_view__when_called__redirects_to_home_page(self):
        response = self.client.post('/accounts/send_login_email', data={
            'email': 'edith@example.com'
        })

        self.assertRedirects(response, '/')


    @patch('accounts.views.send_mail')
    def test__send_email_view__when_called__sends_mail_to_address_from_post(self, mock_send_mail):
        self.client.post('/accounts/send_login_email', data={
            'email': 'edith@example.com'
        })

        self.assertEqual(mock_send_mail.called, True)
        (subject, body, from_email, to_list), kwargs = mock_send_mail.call_args
        self.assertEqual(subject, 'Your login link for Superlists')
        self.assertEqual(from_email, 'noreply@superlists')
        self.assertEqual(to_list, ['edith@example.com'])


    def test__send_email_view__when_successful__adds_success_message(self):
        response = self.client.post('/accounts/send_login_email', data={
            'email': 'edith@example.com'
        }, follow=True)
        message = list(response.context['messages'])[0]

        self.assertEqual(
            message.message,
            "Check your email, we've sent you a link you can use to log in."
        )
        self.assertEqual(message.tags, "success")

    def test__send_email_view__when_successful__creates_token_associated_with_email(self):
        self.client.post('/accounts/send_login_email', data={
            'email': 'edith@example.com'
        })
        token = Token.objects.first()

        self.assertEqual(token.email, 'edith@example.com')

    @patch('accounts.views.send_mail')
    def test__send_email_view__when_successful__sends_link_to_login_using_token_uid(self, mock_send_mail):
        self.client.post('/accounts/send_login_email', data={
            'email': 'edith@example.com'
        })
        token = Token.objects.first()

        expected_url = 'http://testserver/accounts/login?token={}'.format(token.uid)
        (subject, body, from_email, to_list), kwargs = mock_send_mail.call_args

        self.assertIn(expected_url, body)


class LoginViewTest(TestCase):

    def test__login_view__when_called__redirects_to_home_page(self):
        response = self.client.post('/accounts/login?token=abcd123')

        self.assertRedirects(response, '/')
