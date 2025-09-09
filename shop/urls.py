from django.urls import path
from . import views

urlpatterns = [
    path("", views.shop_view, name="shop"),
    path("checkout/<int:product_id>/<int:size_id>/", views.checkout_view, name="checkout"),
    path("", views.shop_view, name="shop"),  # http://127.0.0.1:8000/shop/
    path("payment/<int:product_id>/", views.checkout_view, name="payment"),

]


