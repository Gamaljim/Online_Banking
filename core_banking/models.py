from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
import random
import string
# Create your models here.

class BankAccount(models.Model):
    class AccountChoices(models.TextChoices):
        SAVINGS = 'Savings'
        CURRENT = 'Current'
        BUSINESS = 'Business'

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bank_accounts')
    account_number = models.CharField(max_length=20, unique=True, editable=False)
    account_type = models.CharField(max_length=20, choices=AccountChoices.choices, default=AccountChoices.SAVINGS)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, validators=[MinValueValidator(0.00)])
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.account_number} - {self.account_type}"

    def save(self, *args, **kwargs):
        if not self.account_number:
            self.account_number = self.generate_account_number()
        super().save(*args, **kwargs)

    def generate_account_number(self):
        while True:
            account_number = ''.join(random.choices(string.digits, k=10))
            if not BankAccount.objects.filter(account_number=account_number).exists():
                return account_number
            

class Wallet(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wallet')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, validators=[MinValueValidator(0.00)])

class Transcation(models.Model):
    # learn race condition, learn transcation automicty and database locks
    # increase recipant , and decrease sender , generate transcation reciet , remove git , add slack msgs to notebook
    #recipant = #bank account
    #sender = #bank account
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.00)])
    created_at = models.DateTimeField(auto_now_add=True)