from django.urls import path

from .views import (
    BankAccountCreateView,
    BankAccountListView,
    CreateTransactionView,
    DepositWithdrawView,
    HomeView,
)

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("create-account/", BankAccountCreateView.as_view(), name="create_account"),
    path("account-list/", BankAccountListView.as_view(), name="account_list"),
    path(
        "create-transaction/",
        CreateTransactionView.as_view(),
        name="create_transaction",
    ),
    path("deposit-withdraw/", DepositWithdrawView.as_view(), name="depost-withdraw"),
]
