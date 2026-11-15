from django.test import TestCase, Client
from django.conf import settings
from django.urls import reverse
from django.middleware.csrf import _get_new_csrf_string, _mask_cipher_secret
from sms_app.forms import SMSComposeForm
from django import forms


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

    def test_post_valid_data_redirects_to_home_prg_pattern(self):
        """Verify valid POST redirects to home (PRG pattern) with 302."""
        payload = {
            'phone_number': '09171234567',
            'message': 'Test valid SMS message',
        }
        response = self.client.post(reverse('home'), data=payload)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))

    def test_post_valid_data_follow_redirect_displays_success_flash_message(self):
        """Verify following valid POST redirect provides 200 and success flash message."""
        payload = {
            'phone_number': '+639171234567',
            'message': 'Hello from automated test',
        }
        response = self.client.post(reverse('home'), data=payload, follow=True)
        self.assertEqual(response.status_code, 200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(
            str(messages_list[0]),
            'Message queued for dispatch to +639171234567.'
        )
        self.assertEqual(messages_list[0].tags, 'success')
        self.assertContains(response, 'Message queued for dispatch to +639171234567.')

    def test_post_valid_data_sanitized_number_in_success_message(self):
        """Verify sanitized phone number is formatted and used in the success flash message."""
        payload = {
            'phone_number': '+63 917-123-4567',
            'message': 'Formatted number test',
        }
        response = self.client.post(reverse('home'), data=payload, follow=True)
        self.assertEqual(response.status_code, 200)
        messages_list = list(response.context['messages'])
        self.assertEqual(
            str(messages_list[0]),
            'Message queued for dispatch to +639171234567.'
        )

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

    def test_csrf_enforcement_accepts_post_with_valid_token(self):
        """Verify CSRF middleware allows POST with matching CSRF cookie and form token."""
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

    def test_csrf_enforcement_accepts_post_with_valid_token_in_header(self):
        """Verify CSRF middleware allows POST with matching CSRF cookie and X-CSRFToken header."""
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
