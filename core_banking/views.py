from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, TemplateView

from .forms import BankAccountForm, DepositWithdrawForm, TransactionForm
from .models import BankAccount, Transaction, Wallet

# Create your views here.


class HomeView(TemplateView):
    template_name = "main_bank/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            if Wallet.objects.filter(user=self.request.user).exists():
                context["wallet"] = self.request.user.wallet

        return context


class BankAccountCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = BankAccount
    form_class = BankAccountForm
    template_name = "main_bank/create_bank_account.html"
    success_url = reverse_lazy("home")
    success_message = "Bank account created successfully"

    def form_valid(self, form):
        account = form.save(commit=False)
        account.owner = self.request.user
        account.save()

        return super().form_valid(form)


class BankAccountListView(LoginRequiredMixin, ListView):
    model = BankAccount
    template_name = "main_bank/bank_account_list.html"
    context_object_name = "accounts"

    def get_queryset(self):
        return BankAccount.objects.filter(owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if Wallet.objects.filter(user=self.request.user).exists():
            context["wallet"] = self.request.user.wallet
        return context


class CreateTransactionView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Transaction
    form_class = TransactionForm
    template_name = "main_bank/create_transaction.html"
    success_url = reverse_lazy("home")
    success_message = "Transaction created successfully!"

    def get_form(self, form_class=None):
        """
        Calling this method to initialize the form before it's shown to filter 'sender_bank_account'
        to show only current logged in user's bank accounts
        """
        form = super().get_form(form_class)
        user_accounts = BankAccount.objects.filter(owner=self.request.user)
        form.fields["sender_bank_account"].queryset = user_accounts
        return form

    def form_valid(self, form):
        """
        Called after the form is submitted and validated
        1- Set the sender to currently logged in user
        2- Try saving the transaction to trigger logic in model.save()
        """
        transaction = form.save(commit=False)
        transaction.sender = self.request.user
        try:
            # try to save
            transaction.save()
        # except ValidationError as e:
        #     form.add_error(self.request, e)
        #     return self.form_invalid(form) #Re-display the form with errors

        # which one is better
        except ValueError as e:
            # If the model's save() raised a ValueError (e.g., insufficient funds),
            # we catch it and turn it into a form error:
            form.add_error(None, str(e))  # attaches error message to non_field_errors
            return self.form_invalid(form)
        return redirect(self.success_url)


class DepositWithdrawView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Transaction
    form_class = DepositWithdrawForm
    template_name = "main_bank/deposit_withdraw.html"
    success_url = reverse_lazy("home")
    success_message = "Operation completed Successfully"

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # filter bank account for logged in user
        user_accounts = BankAccount.objects.filter(owner=self.request.user)
        form.fields["sender_bank_account"].queryset = user_accounts
        return form

    def form_valid(self, form):
        transaction = form.save(commit=False)
        transaction.sender = self.request.user

        try:
            transaction.save()
        except ValueError as e:
            form.add_error(None, e)
            return self.form_invalid(form)

        return redirect(self.success_url)
