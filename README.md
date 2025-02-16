# Django Banking Project

A simple Django-based banking application that handles user registration, email activation, wallets, bank accounts, and transactions (deposit, withdrawal, and user-to-user transfers).

## Features
- **Custom User Model** with extended fields (phone, address, etc.).
- **Email Activation**: users receive a token link to confirm their account.
- **Wallet**: automatically created for each user via signals.
- **Bank Accounts**: multiple accounts per user (Savings, Current, Business).
- **Transactions**: deposit, withdrawal, or transfer (wallet-to-wallet/bank-to-bank).
- **Transaction History**: track all completed transactions in a user-friendly list view.


## Users App Overview

### CustomUser Model
- Inherits from **`AbstractBaseUser`** & **`PermissionsMixin`**, with fields like `email`, `first_name`, `last_name`, `phone_number`, etc.
- `is_active=False` by default to enforce email activation.

### Email Activation
- On registration (**`UserRegistrationView`**), the user gets an **activation email** with a unique token.
- The **`activate_account`** view decodes the user’s ID and verifies the token before activating the user.

### Signals
- **`create_user_wallet`**: a `post_save` signal that automatically creates a **`Wallet`** for each new user.

### Key Files
- **`models.py`**: Defines `CustomUser` and `UserManager`.
- **`forms.py`**: `UserRegistrationForm` with password confirmation logic.
- **`views.py`**: `UserRegistrationView`, `activate_account`, `EditProfileView`, etc.
- **`urls.py`**: Routes for `/register/`, `/edit-profile/`, `/activate/<uidb64>/<token>/`, etc.

---

## Core_Banking App Overview

### Models

- **`BankAccount`**
  Linked to `CustomUser` (via `owner`). Stores `balance` and an auto-generated `account_number`.

- **`Wallet`**
  One-to-one with each user. Tracks a separate `balance`.

- **`Transaction`**
  - Represents a deposit, withdrawal, or transfer.
  - `transaction_type` = **Wallet** or **Bank Account**.
  - `transaction_category` = **Deposit**, **Withdrawal**, or empty for transfers.
  - Private helper methods `_handle_deposit()`, `_handle_withdrawal()`, `_handle_transfer()` are called in `save()` to update balances in a **database transaction** (`transaction.atomic()`).
  - A **`receipt`** is auto-generated to identify each transaction uniquely.

### Forms

- **`TransactionForm`**
  For transfers (requires `recipient_address` as an email or bank account number).
- **`DepositWithdrawForm`**
  Simplifies deposit/withdraw by locking `transaction_category` and hiding irrelevant fields.

### Views

- **`BankAccountCreateView`**
  Open new accounts.
- **`BankAccountListView`**
  List user’s accounts.
- **`CreateTransactionView`**
  Old user-to-user or bank-to-bank transfer.
- **`DepositWithdrawView`**
  Deposit/withdraw scenario.
- **`TransactionListView`**
  Shows transaction history, filtering by sender or recipient.
- **`HomeView`**
  Displays a welcome page and wallet balance if logged in.

---

## How Transactions Work

### Transfer
1. User chooses “Wallet” or “Bank Account” and enters recipient info.
2. If **Wallet → Wallet**, funds move from `sender.wallet` to the recipient’s `wallet`.
3. If **Bank → Bank**, funds move from `sender_bank_account` to `recipient_address` (which is a bank account number).

### Deposit
- If **“Wallet”**, we add the deposit amount to the user’s `wallet.balance`.
- If **“Bank Account”**, we add it to the chosen `sender_bank_account`.

### Withdrawal
- If **“Wallet”**, we check if `wallet.balance ≥ amount`, then deduct.
- If **“Bank Account”**, we deduct from the chosen account if sufficient funds exist.
