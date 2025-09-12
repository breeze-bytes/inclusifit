import base64
import requests
import datetime
import json
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from .models import MpesaTransaction
from decimal import Decimal
from shop.models import Product  # Optional if you want to update stock/order

PAYPAL_OAUTH_API = "https://api-m.sandbox.paypal.com/v1/oauth2/token"
PAYPAL_ORDER_API = "https://api-m.sandbox.paypal.com/v2/checkout/orders"

def get_paypal_access_token():
    """Get OAuth token from PayPal"""
    response = requests.post(
        PAYPAL_OAUTH_API,
        auth=(settings.PAYPAL_CLIENT_ID, settings.PAYPAL_SECRET),
        data={"grant_type": "client_credentials"}
    )
    response.raise_for_status()
    return response.json()["access_token"]


from django.shortcuts import render, redirect
from django.conf import settings

def paypal_payment(request):
    # Get amount from GET or POST
    amount = request.GET.get('amount') or request.POST.get('amount')
    
    if not amount:
        amount = 0  # fallback if no amount provided

    return render(request, 'payments/paypal.html', {
        'amount': amount
    })



@csrf_exempt
def paypal_capture(request):
    """Capture completed PayPal order"""
    if request.method == "POST":
        data = json.loads(request.body)
        order_id = data.get("orderID")
        token = get_paypal_access_token()

        # Capture the order
        response = requests.post(
            f"{PAYPAL_ORDER_API}/{order_id}/capture",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            }
        )
        result = response.json()
        if response.status_code == 201:
            # Here you can update your cart/order
            # e.g., mark items as purchased, reduce stock, etc.
            return JsonResponse({"status": "success", "details": result})
        else:
            return JsonResponse({"status": "error", "details": result})

    return JsonResponse({"status": "invalid method"}, status=400)


# ----------------- Helpers -----------------
def get_mpesa_token():
    """Get Daraja OAuth token (sandbox)."""
    consumer_key = settings.DAR_AJA_CONSUMER_KEY
    consumer_secret = settings.DAR_AJA_CONSUMER_SECRET
    auth_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    resp = requests.get(auth_url, auth=(consumer_key, consumer_secret))
    resp.raise_for_status()
    return resp.json().get("access_token")


def lipa_password(timestamp):
    """Generate base64 encoded password for STK Push."""
    data = settings.MPESA_SHORTCODE + settings.MPESA_PASSKEY + timestamp
    return base64.b64encode(data.encode('utf-8')).decode('utf-8')


# ----------------- Views -----------------
def choose_method(request):
    cart = request.session.get("cart", {})
    total = sum(item["price"] * item["quantity"] for item in cart.values())
    return render(request, "payments/method.html", {"total": total})



def mpesa_stk_push(request):
    """Render STK Push form or initiate payment via POST."""
    if request.method == "POST":
        phone = request.POST.get("phone")
        amount = request.POST.get("amount")
        account_ref = request.POST.get("account_reference", "InclusiFitOrder")

        if not phone or not amount:
            return JsonResponse({"error": "Phone and amount required"}, status=400)

        try:
            token = get_mpesa_token()
        except Exception as e:
            return JsonResponse({"error": "Failed to get token", "details": str(e)}, status=500)

        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        password = lipa_password(timestamp)

        payload = {
            "BusinessShortCode": settings.MPESA_SHORTCODE,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": int(float(amount)),
            "PartyA": phone,
            "PartyB": settings.MPESA_SHORTCODE,
            "PhoneNumber": phone,
            "CallBackURL": settings.MPESA_CALLBACK_URL,
            "AccountReference": account_ref,
            "TransactionDesc": "Payment for InclusiFit order"
        }

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        stk_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
        response = requests.post(stk_url, json=payload, headers=headers)
        data = response.json()

        if response.status_code not in (200, 201):
            return JsonResponse({"error": "Daraja error", "details": data}, status=500)

        # Save transaction
        MpesaTransaction.objects.create(
            merchant_request_id=data.get("MerchantRequestID"),
            checkout_request_id=data.get("CheckoutRequestID"),
            phone=phone,
            amount=float(amount),
            raw_callback=data
        )

        return JsonResponse({"message": "STK Push initiated", "daraja_response": data})

    else:
        # GET -> render form
        total_amount = request.GET.get("amount", "")
        return render(request, "payments/mpesa.html", {"total_amount": total_amount})


@csrf_exempt
def mpesa_callback(request):
    """Handle asynchronous STK Push result from Daraja."""
    try:
        body = json.loads(request.body.decode("utf-8"))
    except Exception:
        return HttpResponse(status=400)

    stk_callback = body.get("Body", {}).get("stkCallback", body)
    checkout_request_id = stk_callback.get("CheckoutRequestID")
    merchant_request_id = stk_callback.get("MerchantRequestID")
    result_code = stk_callback.get("ResultCode")
    result_desc = stk_callback.get("ResultDesc")

    # Extract metadata
    callback_items = stk_callback.get("CallbackMetadata", {}).get("Item", [])
    phone, amount = None, None
    for item in callback_items:
        if item.get("Name") == "Amount":
            amount = item.get("Value")
        if item.get("Name") == "PhoneNumber":
            phone = item.get("Value")

    tx, _ = MpesaTransaction.objects.get_or_create(
        checkout_request_id=checkout_request_id,
        defaults={
            "merchant_request_id": merchant_request_id,
            "phone": phone,
            "amount": amount,
            "result_code": result_code,
            "result_desc": result_desc,
            "raw_callback": body
        }
    )

    # Update if exists
    tx.result_code = result_code
    tx.result_desc = result_desc
    if phone: tx.phone = phone
    if amount: tx.amount = amount
    tx.raw_callback = body
    tx.save()

    return JsonResponse({"ResultCode": 0, "ResultDesc": "Accepted"})


def bank_payment(request):
    """Render placeholder bank payment page."""
    return render(request, "payments/bank.html")



