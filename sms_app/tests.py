from django.test import TestCase, Client
from django.conf import settings
from django.urls import reverse
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
