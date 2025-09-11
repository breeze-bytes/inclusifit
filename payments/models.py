from django.db import models

class MpesaTransaction(models.Model):
    merchant_request_id = models.CharField(max_length=200, blank=True, null=True)
    checkout_request_id = models.CharField(max_length=200, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    result_code = models.IntegerField(null=True, blank=True)
    result_desc = models.TextField(blank=True, null=True)
    raw_callback = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"MPESA {self.checkout_request_id} ({self.phone})"
