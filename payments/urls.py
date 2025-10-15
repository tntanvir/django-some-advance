from django.urls import path
from .views import *

urlpatterns = [
    path("create-payment-intent/", CreateCheckoutSessionView.as_view(), name="create-payment"),
    path("webhook/", StripeWebhookView.as_view(), name="stripe-webhook"),
]
