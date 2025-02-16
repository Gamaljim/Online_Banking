from django.contrib import admin

from .models import BankAccount, Transaction, Wallet

# Register your models here.


@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    list_display = [
        "account_number",
        "account_type",
        "balance",
        "is_active",
        "created_at",
        "owner__email",
    ]
    list_filter = ["account_type", "is_active"]


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ["user", "balance", "last_update"]


@admin.register(Transaction)
class transactionAdmin(admin.ModelAdmin):
    list_display = [
        "sender",
        "transaction_type",
        "transaction_category",
        "transaction_status",
        "amount",
        "receipt",
        "created_at",
    ]
    list_filter = ["transaction_type", "transaction_category", "transaction_status"]
    search_fields = ["receipt", "sender__email", "recipient_address"]
    ordering = ["-created_at"]
