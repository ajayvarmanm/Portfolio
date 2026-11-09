import json

from django.test import TestCase, override_settings

from .models import Contact


@override_settings(ALLOWED_FRONTEND_ORIGINS=["https://ajayvarmanm.github.io"])
class ContactApiTests(TestCase):
    def setUp(self):
        self.url = "/api/contact/"
        self.origin = {"HTTP_ORIGIN": "https://ajayvarmanm.github.io"}

    def test_valid_message_is_saved(self):
        response = self.client.post(
            self.url,
            data=json.dumps({
                "name": "Test Visitor",
                "email": "visitor@example.com",
                "message": "Hello from the portfolio."
            }),
            content_type="application/json",
            **self.origin
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Contact.objects.count(), 1)

    def test_unapproved_origin_is_rejected(self):
        response = self.client.post(
            self.url,
            data=json.dumps({"name": "Visitor", "email": "visitor@example.com", "message": "Hi"}),
            content_type="application/json",
            HTTP_ORIGIN="https://unknown.example"
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Contact.objects.count(), 0)

    def test_invalid_email_is_rejected(self):
        response = self.client.post(
            self.url,
            data=json.dumps({"name": "Visitor", "email": "not-an-email", "message": "Hi"}),
            content_type="application/json",
            **self.origin
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Contact.objects.count(), 0)

    def test_honeypot_is_not_saved(self):
        response = self.client.post(
            self.url,
            data=json.dumps({"name": "Bot", "email": "bot@example.com", "message": "Spam", "website": "spam"}),
            content_type="application/json",
            **self.origin
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Contact.objects.count(), 0)
