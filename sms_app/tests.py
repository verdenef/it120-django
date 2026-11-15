from unittest.mock import patch, MagicMock
from django.test import TestCase, Client, override_settings
from django.conf import settings
from django.urls import reverse
from django.middleware.csrf import _get_new_csrf_string, _mask_cipher_secret
from sms_app.forms import SMSComposeForm
from django import forms
import requests
from django.contrib import admin

from sms_app.models import SMSLog
from sms_app.services.textbee import send_sms, TextbeeResult


class ConfigurationSecurityTests(TestCase):
    """
    Verifies settings, secret isolation, and defensive defaults
    as defined in ConfigurationSecurity.md.
    """

    def test_settings_loaded_properly(self):
        """Verify essential Django settings are defined."""
        self.assertTrue(hasattr(settings, 'SECRET_KEY'))
        self.assertTrue(len(settings.SECRET_KEY) > 0)
        self.assertTrue(hasattr(settings, 'ALLOWED_HOSTS'))
        self.assertIn('127.0.0.1', settings.ALLOWED_HOSTS)

    def test_textbee_configuration_variables_exist(self):
        """Verify Textbee gateway configuration attributes are present in settings."""
        self.assertTrue(hasattr(settings, 'TEXTBEE_API_KEY'))
        self.assertTrue(hasattr(settings, 'TEXTBEE_DEVICE_ID'))
        self.assertTrue(hasattr(settings, 'TEXTBEE_BASE_URL'))
        self.assertEqual(settings.TEXTBEE_BASE_URL, 'https://api.textbee.dev/api/v1')

    def test_csrf_middleware_installed(self):
        """Verify CSRF protection middleware is enabled."""
        self.assertIn(
            'django.middleware.csrf.CsrfViewMiddleware',
            settings.MIDDLEWARE
        )


class ViewSmokeTests(TestCase):
    """
    Verifies base shell template rendering and HTTP routing.
    """

    def setUp(self):
        self.client = Client()

    def test_home_page_renders_successfully(self):
        """Verify GET / returns 200 and loads base & home templates."""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'base.html')
        self.assertTemplateUsed(response, 'sms_app/home.html')
        self.assertContains(response, 'Textbee SMS Sender')

    def test_secret_key_not_leaked_in_response(self):
        """Verify sensitive credentials are never leaked in rendered HTML."""
        response = self.client.get(reverse('home'))
        self.assertNotContains(response, settings.SECRET_KEY)
        if settings.TEXTBEE_API_KEY:
            self.assertNotContains(response, settings.TEXTBEE_API_KEY)


class SMSComposeFormTests(TestCase):
    """
    Unit tests for SMSComposeForm validating phone number formats,
    message constraints, widget attributes, and sanitization.
    """

    def test_valid_phone_number_philippine_local(self):
        """Verify Philippine local mobile format (09XXXXXXXXX) is accepted."""
        form = SMSComposeForm(data={
            'phone_number': '09171234567',
            'message': 'Test message'
        })
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['phone_number'], '09171234567')

    def test_valid_phone_number_philippine_international(self):
        """Verify Philippine international mobile format (+639XXXXXXXXX) is accepted."""
        form = SMSComposeForm(data={
            'phone_number': '+639171234567',
            'message': 'Test message'
        })
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['phone_number'], '+639171234567')

    def test_valid_phone_number_standard_international(self):
        """Verify standard E.164 international numbers are accepted."""
        form = SMSComposeForm(data={
            'phone_number': '+14155552671',
            'message': 'Test message'
        })
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['phone_number'], '+14155552671')

    def test_phone_number_sanitization_removes_spaces_and_hyphens(self):
        """Verify formatting characters like spaces and hyphens are stripped during cleaning."""
        form = SMSComposeForm(data={
            'phone_number': '+63 917-123-4567',
            'message': 'Test message'
        })
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['phone_number'], '+639171234567')

        form_local = SMSComposeForm(data={
            'phone_number': '0917-123-4567',
            'message': 'Test message'
        })
        self.assertTrue(form_local.is_valid(), form_local.errors)
        self.assertEqual(form_local.cleaned_data['phone_number'], '09171234567')

    def test_invalid_phone_number_with_letters_rejected(self):
        """Verify phone numbers containing alphabetic characters are rejected."""
        form = SMSComposeForm(data={
            'phone_number': '0917abc4567',
            'message': 'Test message'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('phone_number', form.errors)
        self.assertIn(
            'Enter a valid mobile phone number (e.g., +639171234567 or 09171234567).',
            form.errors['phone_number']
        )

    def test_invalid_phone_number_too_short_rejected(self):
        """Verify phone numbers that are too short are rejected."""
        form = SMSComposeForm(data={
            'phone_number': '091712',
            'message': 'Test message'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('phone_number', form.errors)
        self.assertIn(
            'Enter a valid mobile phone number (e.g., +639171234567 or 09171234567).',
            form.errors['phone_number']
        )

    def test_invalid_phone_number_too_long_rejected(self):
        """Verify phone numbers that are too long are rejected."""
        form = SMSComposeForm(data={
            'phone_number': '+639171234567890123',
            'message': 'Test message'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('phone_number', form.errors)
        self.assertIn(
            'Enter a valid mobile phone number (e.g., +639171234567 or 09171234567).',
            form.errors['phone_number']
        )

    def test_invalid_phone_number_invalid_prefix_rejected(self):
        """Verify phone numbers with invalid local prefixes (e.g. 08XXXXXXXXX) are rejected."""
        form = SMSComposeForm(data={
            'phone_number': '08171234567',
            'message': 'Test message'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('phone_number', form.errors)
        self.assertIn(
            'Enter a valid mobile phone number (e.g., +639171234567 or 09171234567).',
            form.errors['phone_number']
        )

    def test_invalid_phone_number_internal_plus_sign_rejected(self):
        """Verify phone numbers with non-leading '+' characters are rejected."""
        form = SMSComposeForm(data={
            'phone_number': '0917+1234567',
            'message': 'Test message'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('phone_number', form.errors)
        self.assertIn(
            'Enter a valid mobile phone number (e.g., +639171234567 or 09171234567).',
            form.errors['phone_number']
        )

    def test_invalid_phone_number_with_disallowed_symbols_rejected(self):
        """Verify phone numbers with characters other than digits, leading '+', spaces, or hyphens are rejected."""
        form = SMSComposeForm(data={
            'phone_number': '(0917) 123-4567',
            'message': 'Test message'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('phone_number', form.errors)
        self.assertIn(
            'Enter a valid mobile phone number (e.g., +639171234567 or 09171234567).',
            form.errors['phone_number']
        )

    def test_blank_phone_number_rejected(self):
        """Verify blank recipient phone number triggers required error message."""
        form = SMSComposeForm(data={
            'phone_number': '',
            'message': 'Test message'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('phone_number', form.errors)
        self.assertIn('Recipient phone number is required.', form.errors['phone_number'])

    def test_whitespace_phone_number_rejected(self):
        """Verify whitespace-only recipient phone number triggers required error message."""
        form = SMSComposeForm(data={
            'phone_number': '   ',
            'message': 'Test message'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('phone_number', form.errors)
        self.assertIn('Recipient phone number is required.', form.errors['phone_number'])

    def test_blank_message_rejected(self):
        """Verify blank message triggers custom empty error message."""
        form = SMSComposeForm(data={
            'phone_number': '09171234567',
            'message': ''
        })
        self.assertFalse(form.is_valid())
        self.assertIn('message', form.errors)
        self.assertIn('Message body cannot be empty.', form.errors['message'])

    def test_whitespace_only_message_rejected(self):
        """Verify whitespace-only message triggers custom empty error message."""
        form = SMSComposeForm(data={
            'phone_number': '09171234567',
            'message': '   \n  \t  '
        })
        self.assertFalse(form.is_valid())
        self.assertIn('message', form.errors)
        self.assertIn('Message body cannot be empty.', form.errors['message'])

    def test_message_exceeding_160_chars_rejected(self):
        """Verify message longer than 160 characters is rejected."""
        form = SMSComposeForm(data={
            'phone_number': '09171234567',
            'message': 'x' * 161
        })
        self.assertFalse(form.is_valid())
        self.assertIn('message', form.errors)

    def test_message_at_exact_160_chars_accepted(self):
        """Verify message at exactly 160 characters is accepted."""
        content = 'a' * 160
        form = SMSComposeForm(data={
            'phone_number': '09171234567',
            'message': content
        })
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['message'], content)

    def test_message_whitespace_stripped_in_cleaned_data(self):
        """Verify leading and trailing whitespace in message is stripped."""
        form = SMSComposeForm(data={
            'phone_number': '09171234567',
            'message': '  Hello, this is a test.  '
        })
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['message'], 'Hello, this is a test.')

    def test_form_widget_attributes(self):
        """Verify widgets and their HTML attributes match specification."""
        form = SMSComposeForm()
        phone_widget = form.fields['phone_number'].widget
        self.assertIsInstance(phone_widget, forms.TextInput)
        self.assertEqual(phone_widget.attrs.get('class'), 'form-control')
        self.assertEqual(
            phone_widget.attrs.get('placeholder'),
            'e.g. +639171234567 or 09171234567'
        )

        message_widget = form.fields['message'].widget
        self.assertIsInstance(message_widget, forms.Textarea)
        self.assertEqual(message_widget.attrs.get('class'), 'form-control')
        self.assertEqual(message_widget.attrs.get('rows'), 4)
        self.assertEqual(str(message_widget.attrs.get('maxlength')), '160')
        self.assertEqual(
            message_widget.attrs.get('placeholder'),
            'Type your message here...'
        )


class SMSComposeViewTests(TestCase):
    """
    Tests for the SMS composition view logic, routing, PRG pattern,
    Django flash messages, and CSRF protection enforcement.
    """

    def setUp(self):
        self.client = Client()

    def test_get_home_view_returns_200_and_provides_unbound_form(self):
        """Verify GET / returns 200 and passes unbound SMSComposeForm in context."""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'sms_app/home.html')
        self.assertTemplateUsed(response, 'base.html')
        self.assertIn('form', response.context)
        form = response.context['form']
        self.assertIsInstance(form, SMSComposeForm)
        self.assertFalse(form.is_bound)

    @patch('sms_app.views.send_sms')
    def test_post_valid_data_redirects_to_home_prg_pattern(self, mock_send_sms):
        """Verify valid POST redirects to home (PRG pattern) with 302."""
        mock_send_sms.return_value = TextbeeResult(success=True, message_id='batch_test123')
        payload = {
            'phone_number': '09171234567',
            'message': 'Test valid SMS message',
        }
        response = self.client.post(reverse('home'), data=payload)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))
        mock_send_sms.assert_called_once_with('09171234567', 'Test valid SMS message')

    @patch('sms_app.views.send_sms')
    def test_post_valid_data_follow_redirect_displays_success_flash_message(self, mock_send_sms):
        """Verify following valid POST redirect provides 200 and success flash message."""
        mock_send_sms.return_value = TextbeeResult(success=True, message_id='batch_test123')
        payload = {
            'phone_number': '+639171234567',
            'message': 'Hello from automated test',
        }
        response = self.client.post(reverse('home'), data=payload, follow=True)
        self.assertEqual(response.status_code, 200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        expected_msg = 'SMS dispatched successfully to +639171234567 (ID: batch_test123)!'
        self.assertEqual(
            str(messages_list[0]),
            expected_msg
        )
        self.assertEqual(messages_list[0].tags, 'success')
        self.assertContains(response, expected_msg)
        mock_send_sms.assert_called_once_with('+639171234567', 'Hello from automated test')

    @patch('sms_app.views.send_sms')
    def test_post_valid_data_sanitized_number_in_success_message(self, mock_send_sms):
        """Verify sanitized phone number is formatted and used in the success flash message."""
        mock_send_sms.return_value = TextbeeResult(success=True, message_id='batch_test123')
        payload = {
            'phone_number': '+63 917-123-4567',
            'message': 'Formatted number test',
        }
        response = self.client.post(reverse('home'), data=payload, follow=True)
        self.assertEqual(response.status_code, 200)
        messages_list = list(response.context['messages'])
        expected_msg = 'SMS dispatched successfully to +639171234567 (ID: batch_test123)!'
        self.assertEqual(
            str(messages_list[0]),
            expected_msg
        )
        self.assertContains(response, expected_msg)
        mock_send_sms.assert_called_once_with('+639171234567', 'Formatted number test')

    @patch('sms_app.views.send_sms')
    def test_post_valid_data_success_without_batch_id(self, mock_send_sms):
        """Verify valid POST with successful dispatch lacking batch ID displays success message without ID info."""
        mock_send_sms.return_value = TextbeeResult(success=True, message_id=None)
        payload = {
            'phone_number': '09171234567',
            'message': 'Message without batch ID',
        }
        response = self.client.post(reverse('home'), data=payload, follow=True)
        self.assertEqual(response.status_code, 200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        expected_msg = 'SMS dispatched successfully to 09171234567!'
        self.assertEqual(str(messages_list[0]), expected_msg)
        self.assertEqual(messages_list[0].tags, 'success')
        self.assertContains(response, expected_msg)
        self.assertNotContains(response, '(ID:')
        mock_send_sms.assert_called_once_with('09171234567', 'Message without batch ID')

    @patch('sms_app.views.send_sms')
    def test_post_valid_data_gateway_failure_displays_error_flash_message(self, mock_send_sms):
        """Verify valid POST with gateway failure displays messages.error with failure detail and redirects."""
        mock_send_sms.return_value = TextbeeResult(
            success=False,
            error_message="Authentication failed: Invalid Textbee API key.",
            status_code=401,
        )
        payload = {
            'phone_number': '09171234567',
            'message': 'Valid message',
        }
        response = self.client.post(reverse('home'), data=payload, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.redirect_chain), 1)
        self.assertEqual(response.redirect_chain[0][1], 302)

        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        expected_error = "Failed to send SMS: Authentication failed: Invalid Textbee API key."
        self.assertEqual(str(messages_list[0]), expected_error)
        self.assertEqual(messages_list[0].tags, 'error')
        self.assertContains(response, expected_error)
        self.assertContains(response, 'alert-danger')
        mock_send_sms.assert_called_once_with('09171234567', 'Valid message')

    @patch('sms_app.views.send_sms')
    def test_post_valid_data_gateway_timeout_displays_error_without_500(self, mock_send_sms):
        """Verify valid POST with gateway timeout displays friendly timeout error and does not raise 500 error."""
        mock_send_sms.return_value = TextbeeResult(
            success=False,
            error_message="The request to Textbee gateway timed out. Please try again.",
            status_code=None,
        )
        payload = {
            'phone_number': '+639171234567',
            'message': 'Timeout test message',
        }
        response = self.client.post(reverse('home'), data=payload, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.status_code, 500)

        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        expected_error = "Failed to send SMS: The request to Textbee gateway timed out. Please try again."
        self.assertEqual(str(messages_list[0]), expected_error)
        self.assertEqual(messages_list[0].tags, 'error')
        self.assertContains(response, expected_error)
        self.assertContains(response, 'alert-danger')
        mock_send_sms.assert_called_once_with('+639171234567', 'Timeout test message')

    @patch('sms_app.views.send_sms')
    def test_post_valid_data_gateway_connection_error_displays_friendly_error_and_redirects(self, mock_send_sms):
        """Verify valid POST with gateway connection error displays friendly connectivity error and redirects."""
        mock_send_sms.return_value = TextbeeResult(
            success=False,
            error_message="Unable to reach Textbee gateway. Please check internet connectivity.",
            status_code=None,
        )
        payload = {
            'phone_number': '09171234567',
            'message': 'Connection error test message',
        }
        response = self.client.post(reverse('home'), data=payload, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.redirect_chain), 1)
        self.assertEqual(response.redirect_chain[0][1], 302)

        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        expected_error = "Failed to send SMS: Unable to reach Textbee gateway. Please check internet connectivity."
        self.assertEqual(str(messages_list[0]), expected_error)
        self.assertEqual(messages_list[0].tags, 'error')
        self.assertContains(response, expected_error)
        mock_send_sms.assert_called_once_with('09171234567', 'Connection error test message')

    @patch('sms_app.views.send_sms')
    def test_post_valid_data_gateway_rate_limited_displays_error(self, mock_send_sms):
        """Verify valid POST with gateway 429 rate limit displays appropriate error message."""
        mock_send_sms.return_value = TextbeeResult(
            success=False,
            error_message="Rate limit exceeded or insufficient credits.",
            status_code=429,
        )
        payload = {
            'phone_number': '09171234567',
            'message': 'Rate limit test message',
        }
        response = self.client.post(reverse('home'), data=payload, follow=True)
        self.assertEqual(response.status_code, 200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        expected_error = "Failed to send SMS: Rate limit exceeded or insufficient credits."
        self.assertEqual(str(messages_list[0]), expected_error)
        self.assertContains(response, expected_error)
        mock_send_sms.assert_called_once_with('09171234567', 'Rate limit test message')

    @patch('sms_app.views.send_sms')
    def test_post_valid_data_gateway_device_offline_displays_error(self, mock_send_sms):
        """Verify valid POST with gateway 404 device offline displays appropriate error message."""
        mock_send_sms.return_value = TextbeeResult(
            success=False,
            error_message="Device not registered or offline.",
            status_code=404,
        )
        payload = {
            'phone_number': '09171234567',
            'message': 'Device offline test message',
        }
        response = self.client.post(reverse('home'), data=payload, follow=True)
        self.assertEqual(response.status_code, 200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        expected_error = "Failed to send SMS: Device not registered or offline."
        self.assertEqual(str(messages_list[0]), expected_error)
        self.assertContains(response, expected_error)
        mock_send_sms.assert_called_once_with('09171234567', 'Device offline test message')

    @patch('sms_app.views.send_sms')
    def test_post_valid_form_rerenders_properly_on_get_after_redirect(self, mock_send_sms):
        """Verify form re-renders cleanly as an unbound empty form on GET after PRG redirect."""
        mock_send_sms.return_value = TextbeeResult(success=True, message_id='batch-clean-state')
        payload = {
            'phone_number': '09171234567',
            'message': 'Clean state verification message',
        }
        response = self.client.post(reverse('home'), data=payload, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.redirect_chain), 1)
        self.assertEqual(response.redirect_chain[0][0], reverse('home'))
        self.assertEqual(response.redirect_chain[0][1], 302)

        # Unbound form in context
        self.assertIn('form', response.context)
        form = response.context['form']
        self.assertIsInstance(form, SMSComposeForm)
        self.assertFalse(form.is_bound)
        self.assertFalse(form.errors)

        # Subsequent GET request has no messages (messages consumed)
        get_response = self.client.get(reverse('home'))
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(len(list(get_response.context['messages'])), 0)
        self.assertFalse(get_response.context['form'].is_bound)

    def test_post_invalid_data_blank_fields_rerenders_form_with_errors(self):
        """Verify invalid POST with blank fields re-renders 200 with bound form and errors."""
        payload = {
            'phone_number': '',
            'message': '',
        }
        response = self.client.post(reverse('home'), data=payload)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'sms_app/home.html')
        self.assertIn('form', response.context)
        form = response.context['form']
        self.assertTrue(form.is_bound)
        self.assertFalse(form.is_valid())
        self.assertIn('phone_number', form.errors)
        self.assertIn('Recipient phone number is required.', form.errors['phone_number'])
        self.assertIn('message', form.errors)
        self.assertIn('Message body cannot be empty.', form.errors['message'])

        messages_list = list(response.context['messages'])
        self.assertTrue(any('Please correct the errors below.' in str(m) for m in messages_list))
        self.assertContains(response, 'Please correct the errors below.')

    def test_post_invalid_phone_format_rerenders_with_phone_error(self):
        """Verify invalid phone format re-renders with specific phone error."""
        payload = {
            'phone_number': 'not-a-valid-phone',
            'message': 'Valid message body',
        }
        response = self.client.post(reverse('home'), data=payload)
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertIn('phone_number', form.errors)
        self.assertNotIn('message', form.errors)
        messages_list = list(response.context['messages'])
        self.assertTrue(any('Please correct the errors below.' in str(m) for m in messages_list))

    def test_post_message_exceeding_160_chars_rerenders_with_message_error(self):
        """Verify message exceeding 160 characters re-renders with message error."""
        payload = {
            'phone_number': '09171234567',
            'message': 'm' * 161,
        }
        response = self.client.post(reverse('home'), data=payload)
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertIn('message', form.errors)
        self.assertNotIn('phone_number', form.errors)

    def test_csrf_enforcement_rejects_post_without_token(self):
        """Verify CSRF middleware returns 403 Forbidden on POST lacking CSRF token."""
        csrf_client = Client(enforce_csrf_checks=True)
        response = csrf_client.post(
            reverse('home'),
            data={'phone_number': '09171234567', 'message': 'Test message'}
        )
        self.assertEqual(response.status_code, 403)

    @patch('sms_app.views.send_sms')
    def test_csrf_enforcement_accepts_post_with_valid_token(self, mock_send_sms):
        """Verify CSRF middleware allows POST with matching CSRF cookie and form token."""
        mock_send_sms.return_value = TextbeeResult(success=True, message_id='batch_csrf_token')
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_secret = _get_new_csrf_string()
        csrf_client.cookies[settings.CSRF_COOKIE_NAME] = csrf_secret
        csrf_token = _mask_cipher_secret(csrf_secret)

        response = csrf_client.post(
            reverse('home'),
            data={
                'phone_number': '09171234567',
                'message': 'CSRF verified test message',
                'csrfmiddlewaretoken': csrf_token,
            }
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))
        mock_send_sms.assert_called_once_with('09171234567', 'CSRF verified test message')

    @patch('sms_app.views.send_sms')
    def test_csrf_enforcement_accepts_post_with_valid_token_in_header(self, mock_send_sms):
        """Verify CSRF middleware allows POST with matching CSRF cookie and X-CSRFToken header."""
        mock_send_sms.return_value = TextbeeResult(success=True, message_id='batch_csrf_hdr')
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_secret = _get_new_csrf_string()
        csrf_client.cookies[settings.CSRF_COOKIE_NAME] = csrf_secret
        csrf_token = _mask_cipher_secret(csrf_secret)

        response = csrf_client.post(
            reverse('home'),
            data={
                'phone_number': '09171234567',
                'message': 'CSRF header test message',
            },
            headers={'X-CSRFToken': csrf_token}
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))
        mock_send_sms.assert_called_once_with('09171234567', 'CSRF header test message')


class SMSComposeTemplateUITests(TestCase):
    """
    Integration tests for UI template rendering in home.html,
    verifying Bootstrap 5 components, accessible labels,
    live character counter markup, inline error states, and CSRF protection.
    """

    def setUp(self):
        self.client = Client()

    def test_get_home_renders_composition_card_and_form(self):
        """Verify GET / renders composition card with form, inputs, labels, help text, and counter."""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

        content = response.content.decode('utf-8')

        # Composition card header
        self.assertIn('Compose SMS Message', content)

        # Form element attributes
        self.assertIn('method="post"', content)
        self.assertIn(f'action="{reverse("home")}"', content)

        # CSRF token hidden input
        self.assertIn('name="csrfmiddlewaretoken"', content)

        # Labels
        self.assertIn('for="id_phone_number"', content)
        self.assertIn('Recipient Mobile Number', content)
        self.assertIn('for="id_message"', content)
        self.assertIn('Message Body', content)

        # Inputs
        self.assertIn('name="phone_number"', content)
        self.assertIn('id="id_phone_number"', content)
        self.assertIn('name="message"', content)
        self.assertIn('id="id_message"', content)

        # Help text
        self.assertIn(
            'Enter Philippine mobile (e.g. 09171234567, +639171234567) or international format.',
            content
        )

        # Live character counter elements & accessibility
        self.assertIn('id="char-counter"', content)
        self.assertIn('aria-live="polite"', content)
        self.assertIn('0 / 160', content)
        self.assertIn('Standard SMS segment limit: 160 characters', content)

        # Action buttons
        self.assertIn('Send SMS', content)
        self.assertIn('type="submit"', content)

    def test_invalid_post_renders_inline_phone_error_feedback(self):
        """Verify invalid phone input renders is-invalid class and inline feedback containing error text."""
        payload = {
            'phone_number': 'invalid-phone-number',
            'message': 'Hello this is valid text',
        }
        response = self.client.post(reverse('home'), data=payload)
        self.assertEqual(response.status_code, 200)

        content = response.content.decode('utf-8')

        # Check phone input has is-invalid class
        self.assertIn('is-invalid', content)
        self.assertIn('invalid-feedback', content)
        self.assertIn(
            'Enter a valid mobile phone number (e.g., +639171234567 or 09171234567).',
            content
        )

        # Value preservation
        self.assertIn('value="invalid-phone-number"', content)
        self.assertIn('Hello this is valid text', content)

    def test_invalid_post_renders_inline_message_error_feedback(self):
        """Verify invalid message input renders is-invalid class and inline feedback containing error text."""
        payload = {
            'phone_number': '09171234567',
            'message': '',
        }
        response = self.client.post(reverse('home'), data=payload)
        self.assertEqual(response.status_code, 200)

        content = response.content.decode('utf-8')

        self.assertIn('is-invalid', content)
        self.assertIn('invalid-feedback', content)
        self.assertIn('Message body cannot be empty.', content)

    def test_invalid_post_both_fields_empty_renders_both_errors(self):
        """Verify submitting empty form renders inline error feedback for both fields."""
        payload = {
            'phone_number': '',
            'message': '',
        }
        response = self.client.post(reverse('home'), data=payload)
        self.assertEqual(response.status_code, 200)

        content = response.content.decode('utf-8')

        self.assertIn('Recipient phone number is required.', content)
        self.assertIn('Message body cannot be empty.', content)

    def test_character_counter_script_present(self):
        """Verify the client-side character counter JavaScript is present in the rendered page."""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

        content = response.content.decode('utf-8')

        self.assertIn('char-counter', content)
        self.assertIn('addEventListener', content)
        self.assertIn('input', content)
        self.assertIn('keyup', content)
        self.assertIn('bg-warning', content)
        self.assertIn('bg-danger', content)
        self.assertIn('160', content)
        self.assertIn('140', content)

    @patch('sms_app.views.send_sms')
    def test_post_valid_redirect_resets_form_to_clean_state(self, mock_send_sms):
        """Verify that after PRG redirect upon valid submission, the rendered form is clean and empty."""
        mock_send_sms.return_value = TextbeeResult(success=True, message_id='batch-clean-test')
        payload = {
            'phone_number': '09171234567',
            'message': 'Hello from valid submission test',
        }
        response = self.client.post(reverse('home'), data=payload, follow=True)
        self.assertEqual(response.status_code, 200)

        content = response.content.decode('utf-8')
        # Success message displayed
        self.assertIn('SMS dispatched successfully to 09171234567 (ID: batch-clean-test)!', content)
        # Form fields are clean/empty
        self.assertIn('value=""', content)
        self.assertIn('>0 / 160<', content)
        mock_send_sms.assert_called_once_with('09171234567', 'Hello from valid submission test')

    def test_template_accessibility_attributes(self):
        """Verify WCAG 2.1 AA accessibility features: label associations, ARIA live regions, and semantic roles."""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

        content = response.content.decode('utf-8')

        # Label-to-input association
        self.assertIn('<label for="id_phone_number"', content)
        self.assertIn('<input type="tel"', content)
        self.assertIn('id="id_phone_number"', content)

        self.assertIn('<label for="id_message"', content)
        self.assertIn('<textarea', content)
        self.assertIn('id="id_message"', content)

        # ARIA Live Region for live counter
        self.assertIn('id="char-counter"', content)
        self.assertIn('aria-live="polite"', content)


class TextbeeServiceTests(TestCase):
    """
    Comprehensive unit tests for the Textbee SMS gateway service (sms_app.services.textbee).
    Verifies input validation, header/payload structure, credential isolation,
    error branch handling (400, 401, 404, 429, 500), network resilience (timeouts,
    connection failures, request exceptions), and response parsing without making live requests.
    """

    def setUp(self):
        self.recipient = "+639171234567"
        self.message = "Hello from automated test"
        self.api_key = "test-api-key-xyz-12345"
        self.device_id = "test-device-id-67890"
        self.base_url = "https://api.textbee.dev/api/v1"

    @override_settings(TEXTBEE_API_KEY="")
    def test_missing_api_key_when_argument_none_and_settings_empty(self):
        """Verify error result when API key is None and settings.TEXTBEE_API_KEY is empty."""
        result = send_sms(recipient=self.recipient, message=self.message, api_key=None)
        self.assertFalse(result.success)
        self.assertIn("Textbee API key is not configured", result.error_message)
        self.assertIsNone(result.message_id)

    def test_missing_api_key_when_empty_string(self):
        """Verify error result when API key is provided as empty or whitespace string."""
        for empty_val in ["", "   ", None]:
            with override_settings(TEXTBEE_API_KEY=""):
                result = send_sms(recipient=self.recipient, message=self.message, api_key=empty_val)
                self.assertFalse(result.success)
                self.assertIn("Textbee API key is not configured", result.error_message)

    def test_empty_recipient_validation(self):
        """Verify error result when recipient is empty or whitespace."""
        for empty_recipient in ["", "   "]:
            result = send_sms(recipient=empty_recipient, message=self.message, api_key=self.api_key)
            self.assertFalse(result.success)
            self.assertEqual(result.error_message, "Recipient phone number cannot be empty.")

    def test_empty_message_validation(self):
        """Verify error result when message body is empty or whitespace."""
        for empty_msg in ["", "   "]:
            result = send_sms(recipient=self.recipient, message=empty_msg, api_key=self.api_key)
            self.assertFalse(result.success)
            self.assertEqual(result.error_message, "SMS message content cannot be empty.")

    @patch("sms_app.services.textbee.requests.post")
    def test_successful_send_with_sms_batch_id(self, mock_post):
        """Verify successful dispatch extracts smsBatchId from HTTP 200 response."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "smsBatchId": "batch-alpha-123",
            "status": "in_progress",
        }
        mock_post.return_value = mock_response

        result = send_sms(
            recipient=self.recipient,
            message=self.message,
            api_key=self.api_key,
            device_id=self.device_id,
        )

        self.assertTrue(result.success)
        self.assertEqual(result.message_id, "batch-alpha-123")
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.raw_response, {"smsBatchId": "batch-alpha-123", "status": "in_progress"})
        self.assertIsNone(result.error_message)

    @patch("sms_app.services.textbee.requests.post")
    def test_successful_send_http_201_with_underscore_id(self, mock_post):
        """Verify successful dispatch extracts _id from HTTP 201 response."""
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "_id": "mongo-obj-id-456",
            "success": True,
        }
        mock_post.return_value = mock_response

        result = send_sms(
            recipient=self.recipient,
            message=self.message,
            api_key=self.api_key,
        )

        self.assertTrue(result.success)
        self.assertEqual(result.message_id, "mongo-obj-id-456")
        self.assertEqual(result.status_code, 201)

    @patch("sms_app.services.textbee.requests.post")
    def test_successful_send_with_id_and_batch_id_fallbacks(self, mock_post):
        """Verify message_id extraction fallbacks for 'id' and 'batchId' response fields."""
        # Test 'id' field
        mock_resp1 = MagicMock()
        mock_resp1.status_code = 200
        mock_resp1.json.return_value = {"id": "id-789"}
        mock_post.return_value = mock_resp1

        res1 = send_sms(self.recipient, self.message, api_key=self.api_key)
        self.assertTrue(res1.success)
        self.assertEqual(res1.message_id, "id-789")

        # Test 'batchId' field
        mock_resp2 = MagicMock()
        mock_resp2.status_code = 200
        mock_resp2.json.return_value = {"batchId": "legacy-batch-999"}
        mock_post.return_value = mock_resp2

        res2 = send_sms(self.recipient, self.message, api_key=self.api_key)
        self.assertTrue(res2.success)
        self.assertEqual(res2.message_id, "legacy-batch-999")

    @patch("sms_app.services.textbee.requests.post")
    def test_successful_send_without_batch_id_in_response(self, mock_post):
        """Verify successful dispatch handles 200 response lacking an explicit batch/message ID."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True, "message": "Dispatched"}
        mock_post.return_value = mock_response

        result = send_sms(self.recipient, self.message, api_key=self.api_key)
        self.assertTrue(result.success)
        self.assertIsNone(result.message_id)
        self.assertEqual(result.status_code, 200)

    @patch("sms_app.services.textbee.requests.post")
    def test_request_payload_and_headers_structure_with_device_id(self, mock_post):
        """Verify correct endpoint URL, headers, and JSON body with deviceId."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"smsBatchId": "batch-101"}
        mock_post.return_value = mock_response

        send_sms(
            recipient="  +639171234567  ",
            message="Test message body",
            api_key="secret-api-key-123",
            device_id="my-phone-device-456",
            base_url="https://api.textbee.dev/api/v1/",
            timeout=15,
        )

        mock_post.assert_called_once_with(
            "https://api.textbee.dev/api/v1/gateway/send-sms",
            json={
                "recipients": ["+639171234567"],
                "message": "Test message body",
                "deviceId": "my-phone-device-456",
            },
            headers={
                "x-api-key": "secret-api-key-123",
                "Content-Type": "application/json",
            },
            timeout=15,
        )

    @patch("sms_app.services.textbee.requests.post")
    def test_request_payload_omits_device_id_when_empty_or_none(self, mock_post):
        """Verify payload does NOT include deviceId key when device_id is not provided."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"smsBatchId": "batch-102"}
        mock_post.return_value = mock_response

        send_sms(
            recipient=self.recipient,
            message=self.message,
            api_key=self.api_key,
            device_id="",
        )

        args, kwargs = mock_post.call_args
        self.assertNotIn("deviceId", kwargs["json"])
        self.assertEqual(kwargs["json"]["recipients"], [self.recipient])
        self.assertEqual(kwargs["json"]["message"], self.message)

    @patch("sms_app.services.textbee.requests.post")
    def test_http_401_unauthorized_does_not_leak_api_key(self, mock_post):
        """Verify HTTP 401 returns clear authentication error and does not leak API key."""
        sensitive_key = "super-secret-production-textbee-key-999"
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"message": "Invalid API Key"}
        mock_post.return_value = mock_response

        result = send_sms(
            recipient=self.recipient,
            message=self.message,
            api_key=sensitive_key,
        )

        self.assertFalse(result.success)
        self.assertEqual(result.status_code, 401)
        self.assertEqual(result.error_message, "Authentication failed: Invalid Textbee API key.")
        self.assertNotIn(sensitive_key, result.error_message)
        self.assertNotIn(sensitive_key, str(result.raw_response))

    @patch("sms_app.services.textbee.requests.post")
    def test_http_400_bad_request_extracts_message_or_error(self, mock_post):
        """Verify HTTP 400 extracts custom validation message or fallback."""
        # Subtest 1: 'message' field present
        mock_resp1 = MagicMock()
        mock_resp1.status_code = 400
        mock_resp1.json.return_value = {"message": "Invalid phone number format."}
        mock_post.return_value = mock_resp1

        res1 = send_sms(self.recipient, self.message, api_key=self.api_key)
        self.assertFalse(res1.success)
        self.assertEqual(res1.status_code, 400)
        self.assertEqual(res1.error_message, "Invalid phone number format.")

        # Subtest 2: 'error' field present
        mock_resp2 = MagicMock()
        mock_resp2.status_code = 400
        mock_resp2.json.return_value = {"error": "Malformed payload structure."}
        mock_post.return_value = mock_resp2

        res2 = send_sms(self.recipient, self.message, api_key=self.api_key)
        self.assertFalse(res2.success)
        self.assertEqual(res2.status_code, 400)
        self.assertEqual(res2.error_message, "Malformed payload structure.")

        # Subtest 3: empty json response
        mock_resp3 = MagicMock()
        mock_resp3.status_code = 400
        mock_resp3.json.return_value = {}
        mock_post.return_value = mock_resp3

        res3 = send_sms(self.recipient, self.message, api_key=self.api_key)
        self.assertFalse(res3.success)
        self.assertEqual(res3.status_code, 400)
        self.assertEqual(res3.error_message, "Gateway returned HTTP 400.")

    @patch("sms_app.services.textbee.requests.post")
    def test_http_404_not_found(self, mock_post):
        """Verify HTTP 404 returns not found error detail or fallback."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"message": "Device not registered or offline."}
        mock_post.return_value = mock_response

        result = send_sms(self.recipient, self.message, api_key=self.api_key)
        self.assertFalse(result.success)
        self.assertEqual(result.status_code, 404)
        self.assertEqual(result.error_message, "Device not registered or offline.")

    @patch("sms_app.services.textbee.requests.post")
    def test_http_429_rate_limit_exceeded(self, mock_post):
        """Verify HTTP 429 returns rate limit / quota exhaustion message."""
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.json.return_value = {"error": "Too Many Requests"}
        mock_post.return_value = mock_response

        result = send_sms(self.recipient, self.message, api_key=self.api_key)
        self.assertFalse(result.success)
        self.assertEqual(result.status_code, 429)
        self.assertEqual(result.error_message, "Rate limit exceeded or insufficient credits.")

    @patch("sms_app.services.textbee.requests.post")
    def test_http_500_gateway_error(self, mock_post):
        """Verify HTTP 500 returns friendly gateway error."""
        # With error message in body
        mock_resp1 = MagicMock()
        mock_resp1.status_code = 500
        mock_resp1.json.return_value = {"message": "Internal gateway failure."}
        mock_post.return_value = mock_resp1

        res1 = send_sms(self.recipient, self.message, api_key=self.api_key)
        self.assertFalse(res1.success)
        self.assertEqual(res1.status_code, 500)
        self.assertEqual(res1.error_message, "Internal gateway failure.")

        # With empty body
        mock_resp2 = MagicMock()
        mock_resp2.status_code = 500
        mock_resp2.json.return_value = {}
        mock_post.return_value = mock_resp2

        res2 = send_sms(self.recipient, self.message, api_key=self.api_key)
        self.assertFalse(res2.success)
        self.assertEqual(res2.status_code, 500)
        self.assertEqual(res2.error_message, "Gateway returned HTTP 500.")

    @patch("sms_app.services.textbee.requests.post")
    def test_timeout_exception_returns_friendly_error(self, mock_post):
        """Verify requests.exceptions.Timeout returns friendly timeout error."""
        mock_post.side_effect = requests.exceptions.Timeout("Connection timed out after 10s")

        result = send_sms(self.recipient, self.message, api_key=self.api_key)
        self.assertFalse(result.success)
        self.assertIsNone(result.status_code)
        self.assertEqual(
            result.error_message,
            "The request to Textbee gateway timed out. Please try again.",
        )

    @patch("sms_app.services.textbee.requests.post")
    def test_connection_error_exception_returns_friendly_error(self, mock_post):
        """Verify requests.exceptions.ConnectionError returns connectivity error."""
        mock_post.side_effect = requests.exceptions.ConnectionError("Name resolution failed")

        result = send_sms(self.recipient, self.message, api_key=self.api_key)
        self.assertFalse(result.success)
        self.assertIsNone(result.status_code)
        self.assertEqual(
            result.error_message,
            "Unable to reach Textbee gateway. Please check internet connectivity.",
        )

    @patch("sms_app.services.textbee.requests.post")
    def test_general_request_exception_returns_error(self, mock_post):
        """Verify requests.exceptions.RequestException returns descriptive network error."""
        mock_post.side_effect = requests.exceptions.RequestException("Generic network failure")

        result = send_sms(self.recipient, self.message, api_key=self.api_key)
        self.assertFalse(result.success)
        self.assertIsNone(result.status_code)
        self.assertIn("Network error communicating with Textbee gateway: RequestException", result.error_message)

    @patch("sms_app.services.textbee.requests.post")
    def test_unexpected_exception_returns_error(self, mock_post):
        """Verify unhandled general exceptions are caught and return descriptive error."""
        mock_post.side_effect = RuntimeError("Fatal hardware failure")

        result = send_sms(self.recipient, self.message, api_key=self.api_key)
        self.assertFalse(result.success)
        self.assertIsNone(result.status_code)
        self.assertIn("Unexpected error: RuntimeError", result.error_message)

    @patch("sms_app.services.textbee.requests.post")
    def test_non_dict_json_response_handling(self, mock_post):
        """Verify non-dict JSON responses (e.g., list, string, integer) do not crash send_sms."""
        # Non-dict on 200
        mock_resp1 = MagicMock()
        mock_resp1.status_code = 200
        mock_resp1.json.return_value = ["item1", "item2"]
        mock_post.return_value = mock_resp1

        res1 = send_sms(self.recipient, self.message, api_key=self.api_key)
        self.assertTrue(res1.success)
        self.assertIsNone(res1.message_id)
        self.assertEqual(res1.raw_response, {})

        # Non-dict on 500
        mock_resp2 = MagicMock()
        mock_resp2.status_code = 500
        mock_resp2.json.return_value = "Internal Error String"
        mock_post.return_value = mock_resp2

        res2 = send_sms(self.recipient, self.message, api_key=self.api_key)
        self.assertFalse(res2.success)
        self.assertEqual(res2.error_message, "Gateway returned HTTP 500.")
        self.assertEqual(res2.raw_response, {})

    @patch("sms_app.services.textbee.requests.post")
    def test_invalid_json_decode_error_handled_gracefully(self, mock_post):
        """Verify invalid non-JSON HTTP responses do not crash JSON parsing."""
        mock_response = MagicMock()
        mock_response.status_code = 502
        mock_response.json.side_effect = ValueError("No JSON object could be decoded")
        mock_post.return_value = mock_response

        result = send_sms(self.recipient, self.message, api_key=self.api_key)
        self.assertFalse(result.success)
        self.assertEqual(result.status_code, 502)
        self.assertEqual(result.error_message, "Gateway returned HTTP 502.")
        self.assertEqual(result.raw_response, {})

    @patch("sms_app.services.textbee.requests.post")
    @override_settings(
        TEXTBEE_API_KEY="settings-configured-api-key",
        TEXTBEE_DEVICE_ID="settings-configured-device-id",
        TEXTBEE_BASE_URL="https://settings.api.endpoint",
    )
    def test_defaults_to_django_settings_when_parameters_omitted(self, mock_post):
        """Verify send_sms falls back to settings attributes when optional arguments are None."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"smsBatchId": "batch-from-settings"}
        mock_post.return_value = mock_response

        result = send_sms(recipient=self.recipient, message=self.message)

        self.assertTrue(result.success)
        mock_post.assert_called_once_with(
            "https://settings.api.endpoint/gateway/send-sms",
            json={
                "recipients": [self.recipient],
                "message": self.message,
                "deviceId": "settings-configured-device-id",
            },
            headers={
                "x-api-key": "settings-configured-api-key",
                "Content-Type": "application/json",
            },
            timeout=10,
        )


class SMSLogModelTests(TestCase):
    """
    Tests for the SMSLog Django model and admin interface.
    """

    def test_sms_log_creation_and_defaults(self):
        """Verify fields, default values, and successful save."""
        log = SMSLog.objects.create(
            recipient="+639171234567",
            message="Test SMS message content",
        )
        self.assertEqual(log.recipient, "+639171234567")
        self.assertEqual(log.message, "Test SMS message content")
        self.assertEqual(log.status, "SENT")
        self.assertEqual(log.gateway_message_id, "")
        self.assertEqual(log.error_message, "")
        self.assertIsNotNone(log.created_at)

    def test_sms_log_str_representation(self):
        """Verify __str__ format includes recipient, status, and formatted date."""
        log = SMSLog.objects.create(
            recipient="09171234567",
            message="Hello World",
            status="SENT",
        )
        str_rep = str(log)
        self.assertIn("09171234567", str_rep)
        self.assertIn("SENT", str_rep)

    def test_sms_log_ordering(self):
        """Verify records are ordered by -created_at descending by default."""
        import time
        log1 = SMSLog.objects.create(recipient="09171111111", message="First")
        time.sleep(0.01)
        log2 = SMSLog.objects.create(recipient="09172222222", message="Second")
        logs = list(SMSLog.objects.all())
        self.assertEqual(logs[0].pk, log2.pk)
        self.assertEqual(logs[1].pk, log1.pk)

    def test_sms_log_admin_registered(self):
        """Verify SMSLog is registered in admin.site with customized ModelAdmin."""
        self.assertIn(SMSLog, admin.site._registry)
        model_admin = admin.site._registry[SMSLog]
        self.assertEqual(
            model_admin.list_display,
            ("recipient", "status", "gateway_message_id", "created_at")
        )
        self.assertEqual(model_admin.list_filter, ("status", "created_at"))
        self.assertEqual(
            model_admin.search_fields,
            ("recipient", "message", "gateway_message_id")
        )


class SMSLogViewIntegrationTests(TestCase):
    """
    Integration tests for SMS dispatch persistence and dashboard log retrieval in views.
    """

    def setUp(self):
        self.client = Client()

    @patch("sms_app.views.send_sms")
    def test_successful_dispatch_creates_sent_log(self, mock_send_sms):
        """Verify successful dispatch creates an SMSLog record with status SENT."""
        mock_send_sms.return_value = TextbeeResult(
            success=True,
            status_code=200,
            message_id="mock-batch-123",
            error_message=None,
        )

        response = self.client.post(
            reverse("home"),
            data={
                "phone_number": "+639171234567",
                "message": "Test successful log creation",
            },
        )
        self.assertRedirects(response, reverse("home"))
        self.assertEqual(SMSLog.objects.count(), 1)
        log = SMSLog.objects.first()
        self.assertEqual(log.recipient, "+639171234567")
        self.assertEqual(log.message, "Test successful log creation")
        self.assertEqual(log.status, "SENT")
        self.assertEqual(log.gateway_message_id, "mock-batch-123")
        self.assertEqual(log.error_message, "")

    @patch("sms_app.views.send_sms")
    def test_failed_dispatch_creates_failed_log(self, mock_send_sms):
        """Verify failed gateway dispatch creates an SMSLog record with status FAILED."""
        mock_send_sms.return_value = TextbeeResult(
            success=False,
            status_code=401,
            message_id=None,
            error_message="Invalid Textbee API Key.",
        )

        response = self.client.post(
            reverse("home"),
            data={
                "phone_number": "+639171234567",
                "message": "Test failed log creation",
            },
        )
        self.assertRedirects(response, reverse("home"))
        self.assertEqual(SMSLog.objects.count(), 1)
        log = SMSLog.objects.first()
        self.assertEqual(log.recipient, "+639171234567")
        self.assertEqual(log.message, "Test failed log creation")
        self.assertEqual(log.status, "FAILED")
        self.assertEqual(log.gateway_message_id, "")
        self.assertEqual(log.error_message, "Invalid Textbee API Key.")

    @patch("sms_app.views.send_sms")
    def test_invalid_form_submission_does_not_create_log(self, mock_send_sms):
        """Verify invalid form submissions do not create spurious database log records."""
        response = self.client.post(
            reverse("home"),
            data={
                "phone_number": "invalid-phone",
                "message": "",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(SMSLog.objects.count(), 0)
        mock_send_sms.assert_not_called()

    def test_home_view_passes_logs_in_context(self):
        """Verify GET / passes recent SMSLog query in template context."""
        log1 = SMSLog.objects.create(recipient="09171111111", message="Message 1")
        log2 = SMSLog.objects.create(recipient="09172222222", message="Message 2")

        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("logs", response.context)
        logs = list(response.context["logs"])
        self.assertEqual(len(logs), 2)
        self.assertEqual(logs[0].pk, log2.pk)
        self.assertEqual(logs[1].pk, log1.pk)

    def test_home_view_limits_logs_to_20_in_context(self):
        """Verify GET / limits dashboard logs queryset to at most 20 records."""
        for i in range(25):
            SMSLog.objects.create(recipient="09170000000", message=f"Message {i}")

        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("logs", response.context)
        self.assertEqual(len(response.context["logs"]), 20)


class SMSLogUIRenderingTests(TestCase):
    """
    Tests for rendering of the SMS message history audit dashboard and empty state.
    """

    def setUp(self):
        self.client = Client()

    def test_empty_state_rendered_when_no_logs(self):
        """Verify GET / renders friendly empty state message when no dispatch logs exist."""
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No SMS messages dispatched yet")
        self.assertNotContains(response, '<table class="table')

    def test_audit_table_renders_sent_log(self):
        """Verify sent SMSLog renders in audit table with success badge and formatted fields."""
        log = SMSLog.objects.create(
            recipient="+639171234567",
            message="Test message sent content",
            status="SENT",
            gateway_message_id="batch-sent-999",
        )
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "+639171234567")
        self.assertContains(response, "Test message sent content")
        self.assertContains(response, "batch-sent-999")
        self.assertContains(response, "bg-success-subtle")
        self.assertContains(response, "Sent")
        self.assertNotContains(response, "No SMS messages dispatched yet")

    def test_audit_table_renders_failed_log(self):
        """Verify failed SMSLog renders in audit table with danger badge and error message snippet."""
        log = SMSLog.objects.create(
            recipient="09187654321",
            message="Test failed message",
            status="FAILED",
            error_message="Invalid Textbee API Key.",
        )
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "09187654321")
        self.assertContains(response, "Test failed message")
        self.assertContains(response, "bg-danger-subtle")
        self.assertContains(response, "Failed")
        self.assertContains(response, "Invalid Textbee API Key.")






