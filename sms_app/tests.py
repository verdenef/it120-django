from django.test import TestCase, Client
from django.conf import settings
from django.urls import reverse


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
