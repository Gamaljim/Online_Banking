from django.contrib import admin
from .models import BankAccount
# Register your models here.

@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    list_display = ['account_number', 'account_type', 'balance', 'is_active', 'created_at', 'owner__email']
    list_filter = ['account_type', 'is_active']
