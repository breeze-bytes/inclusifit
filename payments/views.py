import requests, base64, datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from shop.models import Product, ProductSize, Order

# Replace with your own Daraja credentials
BUSINESS_SHORTCODE = "174379"
PASSKEY = "YOUR_PASSKEY"
CONSUMER_KEY = "YOUR_CONSUMER_KEY"
CONSUMER_SECRET = "YOUR_CONSUMER_SECRET"
CALLBACK_URL = "https://yourdomain.com/payments/callback/"

def generate_token():
    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(url, auth=(CONSUMER_KEY, CONSUMER_SECRET))
    return response.json().get("access_token")

@csrf_exempt
def lipa_na_mpesa_online(request):
    if request.method == "POST":
        product_id = request.POST.get("product_id")
        size_id = request.POST.get("size_id")
        customer_name = request.POST.get("name")
        phone = request.POST.get("phone")

        # get product & size
        product = Product.objects.get(id=product_id)
        size = ProductSize.objects.get(id=size_id)

        # create order (pending)
        order = Order.objects.create(
            customer_name=customer_name,
            phone=phone,
            product=product,
            size=size,
            amount=product.price,
            status="pending",
        )

        # Safaricom API
        token = generate_token()
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        password = base64.b64encode(
            (BUSINESS_SHORTCODE + PASSKEY + timestamp).encode("utf-8")
        ).decode("utf-8")

        payload = {
            "BusinessShortCode": BUSINESS_SHORTCODE,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": str(product.price),
            "PartyA": phone,
            "PartyB": BUSINESS_SHORTCODE,
            "PhoneNumber": phone,
            "CallBackURL": CALLBACK_URL,
            "AccountReference": f"Order{order.id}",
            "TransactionDesc": f"Payment for {product.name} ({size.size})",
        }

        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(
            "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest",
            json=payload,
            headers=headers,
        )
        resp_data = response.json()

        # store CheckoutRequestID in the order
        checkout_id = resp_data.get("CheckoutRequestID")
        if checkout_id:
            order.checkout_request_id = checkout_id
            order.save()

        return JsonResponse(resp_data)

    return JsonResponse({"error": "Invalid request"}, status=400)

@csrf_exempt
def mpesa_callback(request):
    import json
    data = request.body.decode("utf-8")
    json_data = json.loads(data)

    callback = json_data["Body"]["stkCallback"]
    checkout_id = callback["CheckoutRequestID"]
    result_code = callback["ResultCode"]

    # Find the order by checkout_id
    try:
        order = Order.objects.get(checkout_request_id=checkout_id)
    except Order.DoesNotExist:
        return JsonResponse({"error": "Order not found"}, status=404)

    if result_code == 0:
        # Payment success
        metadata = callback["CallbackMetadata"]["Item"]
        transaction_code = None
        for item in metadata:
            if item["Name"] == "MpesaReceiptNumber":
                transaction_code = item["Value"]

        order.status = "paid"
        order.transaction_code = transaction_code
        order.save()
    else:
        # Payment failed/cancelled
        order.status = "failed"
        order.save()

    return JsonResponse({"status": "ok"})
