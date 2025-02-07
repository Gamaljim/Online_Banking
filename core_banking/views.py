from django.views.generic import CreateView, ListView, TemplateView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from .forms import BankAccountForm
from .models import BankAccount

# Create your views here.


class HomeView(TemplateView):
    template_name = 'main_bank/home.html'



class BankAccountCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = BankAccount
    form_class = BankAccountForm
    template_name = 'main_bank/create_bank_account.html'
    success_url = reverse_lazy('home')
    success_message = 'Bank account created successfully'
    def form_valid(self, form):
        account = form.save(commit=False)
        account.owner = self.request.user
        account.save()

        return super().form_valid(form)


class BankAccountListView(LoginRequiredMixin, ListView):
    model = BankAccount
    template_name = 'main_bank/bank_account_list.html'
    context_object_name = 'accounts'

    def get_queryset(self):
        return BankAccount.objects.filter(owner=self.request.user)
    
