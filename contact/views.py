import json

from django.conf import settings
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .models import Contact


@csrf_exempt
@require_POST
def contact_api(request):
    """Accept a small JSON contact message from the public portfolio form."""
    origin = request.headers.get("Origin", "")
    if origin not in settings.ALLOWED_FRONTEND_ORIGINS:
        return JsonResponse({"error": "Origin not allowed."}, status=403)
    if request.content_type != "application/json":
        return JsonResponse({"error": "Send the form as JSON."}, status=415)
    if len(request.body) > 10_000:
        return JsonResponse({"error": "Message is too large."}, status=413)
    try:
        data = json.loads(request.body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return JsonResponse({"error": "Invalid request body."}, status=400)

    if data.get("website"):
        return JsonResponse({"message": "Thanks. Your message has been received."})

    name = str(data.get("name", "")).strip()
    email = str(data.get("email", "")).strip()
    message = str(data.get("message", "")).strip()
    if not name or len(name) > 100:
        return JsonResponse({"error": "Enter a name (up to 100 characters)."}, status=400)
    if not email or len(email) > 254:
        return JsonResponse({"error": "Enter a valid email address."}, status=400)
    try:
        validate_email(email)
    except ValidationError:
        return JsonResponse({"error": "Enter a valid email address."}, status=400)
    if not message or len(message) > 3000:
        return JsonResponse({"error": "Enter a message (up to 3,000 characters)."}, status=400)

    Contact.objects.create(name=name, email=email, message=message)
    return JsonResponse({"message": "Thanks. Your message has been received."}, status=201)
