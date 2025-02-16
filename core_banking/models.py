import random
import string

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models, transaction

# Create your models here.
User = get_user_model()


class BankAccount(models.Model):
    class AccountChoices(models.TextChoices):
        SAVINGS = "Savings"
        CURRENT = "Current"
        BUSINESS = "Business"

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bank_accounts"
    )
    account_number = models.CharField(max_length=20, unique=True, editable=False)
    account_type = models.CharField(
        max_length=20, choices=AccountChoices.choices, default=AccountChoices.SAVINGS
    )
    balance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0.00)],
    )
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
            account_number = "".join(random.choices(string.digits, k=10))
            if not BankAccount.objects.filter(account_number=account_number).exists():
                return account_number


class Wallet(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="wallet"
    )
    balance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0.00)],
    )
    last_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email}'s wallet"


class Transaction(models.Model):
    # i can send directly to a wallet if i have the email
    # i can send directly to any bank account if i have the bank accoutn number
    # i can recieve in the same 2 ways as above
    class TransactionType(models.TextChoices):
        WALLET = "Wallet"
        BANK_ACCOUNT = "Bank Account"

    class TransactionCategory(models.TextChoices):
        DEPOSIT = "Deposit"
        WAITHDRAWAL = "Withdrawal"

    class TransactionStatus(models.TextChoices):
        PENDING = "Pending"
        COMPLETED = "Completed"
        FAILED = "Failed"

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_transactions",
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="received_transactions",
    )
    recipient_address = models.CharField(max_length=300, null=True, blank=True)
    sender_bank_account = models.ForeignKey(
        BankAccount, on_delete=models.SET_NULL, null=True, blank=True
    )

    transaction_type = models.CharField(
        max_length=30, choices=TransactionType.choices, null=True, blank=True
    )
    transaction_category = models.CharField(
        max_length=30, choices=TransactionCategory.choices, null=True, blank=True
    )
    transaction_status = models.CharField(
        max_length=30,
        choices=TransactionStatus.choices,
        default=TransactionStatus.PENDING,
        null=True,
        blank=True,
    )

    amount = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)]
    )
    receipt = models.CharField(max_length=10, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        rec = self.recipient.email if self.recipient else self.recipient_address
        return f"{self.sender.email} sent {self.amount} to {rec}"

    def generate_receipt_number(self):
        while True:
            receipt_number = "".join(random.choices(string.digits, k=5))
            if not Transaction.objects.filter(receipt=receipt_number).exists():
                return receipt_number

    def save(self, *args, **kwargs):
        if not self.receipt:
            self.receipt = self.generate_receipt_number()

        self.transaction_status = self.TransactionStatus.PENDING

        with transaction.atomic():
            if not self.transaction_category:
                self._handle_transfer()
            elif self.transaction_category == self.TransactionCategory.DEPOSIT:
                self._handle_deposit()
            elif self.transaction_category == self.TransactionCategory.WAITHDRAWAL:
                self._handle_withdrawal()
            else:
                raise ValueError("Unsupported transaction category.")

        super().save(*args, **kwargs)

    def _handle_deposit(self):
        """
        If transaction_type == WALLET, deposit to sender's wallet.
        If transaction_type == BANK_ACCOUNT, deposit to sender's bank account.
        """

        if self.transaction_type == self.TransactionType.WALLET:
            wallet = self.sender.wallet
            wallet.balance += self.amount
            wallet.save()
            self.transaction_status = self.TransactionStatus.COMPLETED

        elif self.transaction_type == self.TransactionType.BANK_ACCOUNT:
            if not self.sender_bank_account:
                self.transaction_status = self.TransactionStatus.FAILED
                raise ValueError("No sender bank account specified.")

            bank_account = self.sender_bank_account
            bank_account.balance += self.amount
            bank_account.save()
            self.transaction_status = self.TransactionStatus.COMPLETED

        else:
            raise ValueError("Transaction type not supported")

    def _handle_withdrawal(self):
        """
        If WALLET, withdraw from the sender's wallet.
        If BANK_ACCOUNT, withdraw from the sender's bank account.
        """

        if self.transaction_type == self.TransactionType.WALLET:
            wallet = self.sender.wallet
            if self.amount > wallet.balance:
                self.transaction_status = self.TransactionStatus.FAILED
                raise ValueError(
                    f"You don't have enough funds in your wallet , you wallet balance is {wallet.balance}"
                )

            wallet.balance -= self.amount
            wallet.save()
            self.transaction_status = self.TransactionStatus.COMPLETED

        elif self.transaction_type == self.TransactionType.BANK_ACCOUNT:
            if not self.sender_bank_account:
                self.transaction_status = self.TransactionStatus.FAILED
                raise ValueError("No sender bank account specified.")

            bank_account = self.sender_bank_account
            if self.amount > bank_account.balance:
                self.transaction_status = self.TransactionStatus.FAILED
                raise ValueError(
                    f"you don't have enough funds in your bank account, your bank account balance is {bank_account.balance}"
                )

            bank_account.balance -= self.amount
            bank_account.save()
            self.transaction_status = self.TransactionStatus.COMPLETED

        else:
            raise ValueError("Transaction type not supported")

    def _handle_transfer(self):
        # getting sender and amount from the transaction
        sender = self.sender
        amount = self.amount

        if self.transaction_type == self.TransactionType.WALLET:
            # using wallet
            sender_wallet = sender.wallet
            if amount > sender_wallet.balance:
                self.transaction_status = self.TransactionStatus.FAILED
                raise ValueError(
                    f"You don't have enough funds in your wallet , you wallet balance is {sender_wallet.balance}"
                )

            if not User.objects.filter(email=self.recipient_address).exists():
                self.transaction_status = self.TransactionStatus.FAILED
                raise ValueError(
                    f"User with email {self.recipient_address} does not exist"
                )

            recipient_wallet = User.objects.get(email=self.recipient_address).wallet
            # Deducting money
            sender_wallet.balance -= amount
            sender_wallet.save()
            # adding money
            recipient_wallet.balance += amount
            recipient_wallet.save()
            self.transaction_status = self.TransactionStatus.COMPLETED

        # USING BANK_ACCOUNT
        elif self.transaction_type == self.TransactionType.BANK_ACCOUNT:
            sender_account = self.sender_bank_account
            if not sender_account:
                self.transaction_status = self.TransactionStatus.FAILED
                raise ValueError("No sender bank account specified.")

            if amount > self.sender_bank_account.balance:
                self.transaction_status = self.TransactionStatus.FAILED
                raise ValueError(
                    f"you don't have enough funds in your bank account, your bank account balance is {self.sender_bank_account.balance}"
                )

            try:
                recipiant_bank_account = BankAccount.objects.get(
                    account_number=self.recipient_address
                )
            except BankAccount.DoesNotExist:
                self.transaction_status = self.TransactionStatus.FAILED
                raise ValueError(
                    f"Bank account with account number {self.recipient_address} does not exist"
                )

            if recipiant_bank_account == sender_account:
                self.transaction_status = self.TransactionStatus.FAILED
                raise ValueError("Sender and Recipient bank account cannot be the same")

            # Deducting money
            sender_account.balance -= amount
            sender_account.save()
            # adding money
            recipiant_bank_account.balance += amount
            recipiant_bank_account.save()
            self.transaction_status = self.TransactionStatus.COMPLETED

        else:
            raise ValueError("Transcation Type not supported")
