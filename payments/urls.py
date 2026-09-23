from django.urls import path
from .views import PaymentInitiateView, MockPaymentProcessView,PaymentWebhookView

urlpatterns = [
    path(
        "initiate/",
        PaymentInitiateView.as_view(),
        name="payment-initiate"
    ),
    path(
        "process/<int:pk>/",
        MockPaymentProcessView.as_view(),
        name="payment-process"
    ),
    path(
    "webhook/",
    PaymentWebhookView.as_view(),
    name="payment-webhook"
),
]
