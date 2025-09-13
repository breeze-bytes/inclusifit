from django.views.decorators.csrf import csrf_exempt

from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, ProductSize
import json
from django.http import JsonResponse





@csrf_exempt
def add_to_cart(request, product_id):
    if request.method == "POST":
        product = get_object_or_404(Product, id=product_id)
        data = json.loads(request.body)
        size_id = data.get("size")
        quantity = int(data.get("quantity", 1))

        cart = request.session.get("cart", {})
        key = f"{product_id}_{size_id}"

        if key in cart:
            cart[key]["quantity"] += quantity
        else:
            cart[key] = {
                "product_id": product_id,
                "size_id": size_id,
                "quantity": quantity,
                "price": float(product.price),
                "name": product.name,
            }

        request.session["cart"] = cart
        cart_item_count = sum(item["quantity"] for item in cart.values())

        return JsonResponse({"success": True, "cart_item_count": cart_item_count})
    return JsonResponse({"success": False}, status=400)


def cart_view(request):
    cart = request.session.get("cart", {})
    cart_items = []
    total = 0

    for key, item in cart.items():
        product = get_object_or_404(Product, id=item["product_id"])
        size = get_object_or_404(ProductSize, id=item["size_id"])
        quantity = item["quantity"]
        subtotal = product.price * quantity
        total += subtotal

        cart_items.append({
            "key": key,
            "product": product,
            "size": size,
            "quantity": quantity,
            "subtotal": subtotal,
        })

    return render(request, "shop/cart.html", {
        "cart_items": cart_items,
        "total": total,
    })


def update_cart(request, key):
    if request.method == "POST":
        data = json.loads(request.body)
        action = data.get("action")
        cart = request.session.get("cart", {})

        if key in cart:
            if action == "increment":
                cart[key]["quantity"] += 1
            elif action == "decrement":
                cart[key]["quantity"] = max(1, cart[key]["quantity"] - 1)
            elif action == "delete":
                del cart[key]
                request.session["cart"] = cart
                return JsonResponse({
                    "success": True,
                    "deleted": True,
                    "total": sum(item["quantity"] * item["price"] for item in cart.values())
                })
            
        request.session["cart"] = cart
        return JsonResponse({
            "success": True,
            "quantity": cart[key]["quantity"],
            "subtotal": cart[key]["quantity"] * cart[key]["price"],
            "total": sum(item["quantity"] * item["price"] for item in cart.values())
        })

    return JsonResponse({"success": False}, status=400)


def remove_from_cart(request, key):
    if request.method == "POST":
        cart = request.session.get("cart", {})
        if key in cart:
            del cart[key]
            request.session["cart"] = cart
    return redirect("shop:cart")



def home(request):
    return render(request, "shop/index.html")

def shop_view(request):
    product = get_object_or_404(Product, name="Underwear")  # single product
    cart = request.session.get("cart", {})
    cart_item_count = sum(item["quantity"] for item in cart.values())

    # wrap single product in a list to match template
    products = [product]

    return render(request, "shop/shop.html", {
        "products": products,
        "cart_item_count": cart_item_count,
    })


    product = get_object_or_404(Product, id=product_id)
    size_id = request.GET.get("size")  # get from ?size=2
    if not size_id:
        return render(request, "shop/no_size_selected.html")  # optional
    size = product.sizes.get(id=size_id)
    return render(request, "shop/checkout.html", {"product": product, "size": size})

from django.shortcuts import render

def about(request):
    return render(request, 'about.html')


