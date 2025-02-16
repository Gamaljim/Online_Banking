from decimal import Decimal

from django import forms
from django.core.exceptions import ValidationError

from .models import BankAccount, Transaction


class BankAccountForm(forms.ModelForm):
    class Meta:
        model = BankAccount
        fields = ["account_type", "balance"]


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = [
            "transaction_type",
            "amount",
            "recipient_address",
            "sender_bank_account",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # check if form submitted POST/GET
        if self.data:
            transaction_type = self.data.get("transaction_type")
        else:
            # if an existing instance in self.instance
            transaction_type = self.instance.transaction_type

        if transaction_type == Transaction.TransactionType.WALLET:
            # sending from a wallet to wallet "using email"
            self.fields["sender_bank_account"].required = False
            self.fields["sender_bank_account"].widget = forms.HiddenInput()

            # recipiant address
            self.fields["recipient_address"].label = "Recipiant Email"
            self.fields[
                "recipient_address"
            ].help_text = "Enter the email address of the recipient."

        elif transaction_type == Transaction.TransactionType.BANK_ACCOUNT:
            # sending from a bank account to a bank account
            self.fields["recipient_address"].required = True
            self.fields["recipient_address"].label = "Recipient Bank Account Number"
            self.fields[
                "recipient_address"
            ].help_text = (
                "Enter the bank account number of the person you want to send money to."
            )

        else:
            # if its invalid, we won't force anything yet
            self.fields["sender_bank_account"].required = False
            self.fields["recipient_address"].label = "Recipient Info"

    def clean_amount(self):
        amount = self.cleaned_data.get("amount")
        if amount is None or amount <= Decimal("0.00"):
            raise forms.ValidationError("Amount must be greater than 0.00")
        return amount

    def clean(self):
        cleaned_data = super().clean()
        transaction_type = cleaned_data.get("transaction_type")
        recipient_address = cleaned_data.get("recipient_address")
        sender_bank_account = cleaned_data.get("sender_bank_account")

        if transaction_type == Transaction.TransactionType.WALLET:
            if recipient_address and "@" not in recipient_address:
                self.add_error(  # when to use validationerror and when to use add_eeror
                    "recipient_address", "Please enter a valid email address."
                )
        elif transaction_type == Transaction.TransactionType.BANK_ACCOUNT:
            if not recipient_address:
                self.add_error(
                    "recipient_address", "Please enter a valid bank account number."
                )
            else:
                exists = BankAccount.objects.filter(
                    account_number=recipient_address
                ).exists()
                if not exists:
                    self.add_error("recipient_address", "Bank account does not exist.")
            if not sender_bank_account:
                self.add_error(
                    "sender_bank_account", "Please select a bank account to send from."
                )
            if (
                sender_bank_account
                and recipient_address == sender_bank_account.account_number
            ):
                self.add_error(
                    "recipient_address",
                    "You cannot send money to your own bank account.",
                )

        return cleaned_data


class DepositWithdrawForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = [
            "transaction_category",
            "transaction_type",
            "sender_bank_account",
            "amount",
        ]  # rename sender_bank_account

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # if its a POST req we get what the user chose
        if self.data:
            trans_cat = self.data.get("transaction_category")
            trans_type = self.data.get("transaction_type")

        else:
            # if there's an existing instance ( editing a transaction)
            trans_cat = self.instance.transaction_category
            trans_type = self.instance.transaction_type

        if trans_type == Transaction.TransactionType.WALLET:
            # Hide the bank account field as its not needed for wallet
            self.fields["sender_bank_account"].required = False
            self.fields["sender_bank_account"].widget = forms.HiddenInput()
        elif trans_type == Transaction.TransactionType.BANK_ACCOUNT:
            # Must choose a bank account
            self.fields["sender_bank_account"].required = True
        else:
            self.fields["sender_bank_account"].required = False

        if trans_cat == Transaction.TransactionCategory.DEPOSIT:
            self.fields["transaction_type"].label = "Deposit into (Wallet or Bank)"
        elif trans_cat == Transaction.TransactionCategory.WAITHDRAWAL:
            self.fields["transaction_type"].label = "Withdraw from (Wallet or Bank)"

    def clean_amount(self):
        """
        Validate amount is > 0
        """
        amount = self.cleaned_data.get("amount")
        if amount is None or amount <= Decimal("0.00"):
            raise ValidationError("Amount must be greater than 0.00")
        return amount

    def clean(self):
        """
        Checks that user choices make sense
        """
        cleaned_data = super().clean()
        category = cleaned_data.get("transaction_category")
        ttype = cleaned_data.get("transaction_type")
        sender_bank_account = cleaned_data.get("sender_bank_account")

        if not category:
            self.add_error("transaction_category", "Select a Category")
        if ttype == Transaction.TransactionType.BANK_ACCOUNT:
            if not sender_bank_account:
                self.add_error("sender_bank_account", "Select a Bank Account")

        return cleaned_data
