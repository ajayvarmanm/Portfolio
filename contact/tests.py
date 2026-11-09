import json

from django.core.cache import cache
from django.test import TestCase, override_settings

from .models import Contact


@override_settings(ALLOWED_FRONTEND_ORIGINS=["https://ajayvarmanm.github.io"])
class ContactApiTests(TestCase):
    def setUp(self):
        self.url = "/api/contact/"
        self.origin = {"HTTP_ORIGIN": "https://ajayvarmanm.github.io"}
        cache.clear()

    def post_json(self, payload, **extra):
        return self.client.post(
            self.url,
            data=json.dumps(payload),
            content_type="application/json",
            **self.origin,
            **extra,
        )

    def valid_payload(self):
        return {
            "name": "Test Visitor",
            "email": "visitor@example.com",
            "message": "Hello from the portfolio.",
        }

    def test_valid_message_is_saved(self):
        response = self.post_json(self.valid_payload())
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Contact.objects.count(), 1)

    def test_unapproved_origin_is_rejected(self):
        response = self.client.post(
            self.url,
            data=json.dumps(self.valid_payload()),
            content_type="application/json",
            HTTP_ORIGIN="https://unknown.example",
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Contact.objects.count(), 0)

    def test_missing_origin_is_rejected(self):
        response = self.client.post(
            self.url,
            data=json.dumps(self.valid_payload()),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)

    def test_invalid_email_is_rejected(self):
        payload = self.valid_payload()
        payload["email"] = "not-an-email"
        response = self.post_json(payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Contact.objects.count(), 0)

    def test_honeypot_is_not_saved(self):
        payload = self.valid_payload()
        payload["website"] = "spam"
        response = self.post_json(payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Contact.objects.count(), 0)

    def test_non_object_json_is_rejected(self):
        response = self.client.post(
            self.url,
            data=json.dumps(["not", "an", "object"]),
            content_type="application/json",
            **self.origin,
        )
        self.assertEqual(response.status_code, 400)

    def test_invalid_json_is_rejected(self):
        response = self.client.post(
            self.url,
            data="{invalid",
            content_type="application/json",
            **self.origin,
        )
        self.assertEqual(response.status_code, 400)

    def test_wrong_content_type_is_rejected(self):
        response = self.client.post(
            self.url,
            data="name=Visitor",
            content_type="application/x-www-form-urlencoded",
            **self.origin,
        )
        self.assertEqual(response.status_code, 415)

    def test_oversized_request_is_rejected(self):
        response = self.client.post(
            self.url,
            data=" " * 10_001,
            content_type="application/json",
            **self.origin,
        )
        self.assertEqual(response.status_code, 413)

    def test_rate_limit_blocks_sixth_valid_message(self):
        for _ in range(5):
            response = self.post_json(self.valid_payload())
            self.assertEqual(response.status_code, 201)

        response = self.post_json(self.valid_payload())
        self.assertEqual(response.status_code, 429)
        self.assertEqual(Contact.objects.count(), 5)
