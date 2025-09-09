from django.urls import path
from . import views

urlpatterns = [
    path("stkpush/", views.lipa_na_mpesa_online, name="lipa_na_mpesa_online"),
    path("callback/", views.mpesa_callback, name="mpesa_callback"),

    
]


