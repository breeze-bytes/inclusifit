from django.urls import path
from . import views 
app_name = "shop"


urlpatterns = [
    path("", views.shop_view, name="shop"),
    path("cart/", views.cart_view, name="cart"),
    path("add-to-cart/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("cart/update/<str:key>/", views.update_cart, name="update_cart"),
    path("cart/remove/<str:key>/", views.remove_from_cart, name="remove_from_cart"),

]


