from django.urls import path
from . import views

app_name = "payments"

urlpatterns = [
    path("checkout/", views.choose_method, name="method"),
    path("bank/", views.bank_payment, name="bank"),
    path("paypal/", views.paypal_payment, name="paypal"),
    path("mpesa/stk/", views.mpesa_stk_push, name="mpesa_stk"),
    path("mpesa/callback/", views.mpesa_callback, name="mpesa_callback"),
]
