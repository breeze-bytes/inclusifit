from django.shortcuts import render, get_object_or_404
from .models import Product

def home(request):
    return render(request, "shop/index.html")

def shop_view(request):
    product = get_object_or_404(Product, name="Underwear")  # single product
    return render(request, "shop/shop.html", {"product": product})
def checkout_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    size_id = request.GET.get("size")  # get from ?size=2
    if not size_id:
        return render(request, "shop/no_size_selected.html")  # optional
    size = product.sizes.get(id=size_id)
    return render(request, "shop/checkout.html", {"product": product, "size": size})



