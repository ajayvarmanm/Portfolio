from django.urls import path
from .views import contact_api

urlpatterns = [
    path('api/contact/', contact_api),
]