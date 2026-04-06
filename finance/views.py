import logging

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Transaction
from .forms import TransactionForm
from cloud_finance_lib import CloudFinancialPlatform, TransactionSnapshot
from finance_utils.calculations import total_income, total_expense, balance


logger = logging.getLogger(__name__)


def home(request):
    return render(request, 'finance/home.html')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/accounts/login/')
    else:
        form = UserCreationForm()

    return render(request, 'finance/register.html', {'form': form})


def get_current_user(request):
    """
    Returns:
    - Logged-in user (personal mode)
    - Hidden demo user (public mode, no login required)
    """

    if request.user.is_authenticated:
        return request.user, False

    # 🌐 Public visitor → use hidden demo account
    demo_user, created = User.objects.get_or_create(
        username='public_demo',
        defaults={
            'is_active': True
        }
    )

    return demo_user, True


def dashboard(request):

    current_user, is_public = get_current_user(request)

    transactions = Transaction.objects.filter(user=current_user)

    income = total_income(transactions)
    expense = total_expense(transactions)
    user_balance = balance(transactions)

    return render(request, 'finance/dashboard.html', {
        'transactions': transactions,
        'income': income,
        'expense': expense,
        'balance': user_balance,
        'is_public': is_public
    })


# ➕ ADD TRANSACTION (Public + Personal)
def add_transaction(request):

    current_user, _ = get_current_user(request)

    if request.method == 'POST':
        form = TransactionForm(request.POST, request.FILES)
        if form.is_valid():
            trans = form.save(commit=False)
            trans.user = current_user
            trans.save()
            sync_transaction_to_cloud(trans)
            return redirect('dashboard')
    else:
        form = TransactionForm()

    return render(request, 'finance/add_transaction.html', {'form': form})

# ✏️ UPDATE TRANSACTION
def edit_transaction(request, pk):

    current_user, _ = get_current_user(request)

    transaction = Transaction.objects.get(pk=pk, user=current_user)

    if request.method == 'POST':
        form = TransactionForm(request.POST, request.FILES, instance=transaction)
        if form.is_valid():
            updated_transaction = form.save()
            sync_transaction_to_cloud(updated_transaction)
            return redirect('dashboard')
    else:
        form = TransactionForm(instance=transaction)

    return render(request, 'finance/add_transaction.html', {'form': form})


# 🗑️ DELETE TRANSACTION
def delete_transaction(request, pk):

    current_user, _ = get_current_user(request)

    transaction = Transaction.objects.get(pk=pk, user=current_user)

    if request.method == 'POST':
        transaction.delete()
        return redirect('dashboard')

    return render(request, 'finance/delete_confirm.html', {'transaction': transaction})


def sync_transaction_to_cloud(transaction):
    snapshot = TransactionSnapshot(
        transaction_id=transaction.id,
        user_id=transaction.user_id,
        title=transaction.title,
        amount=transaction.amount,
        currency=transaction.currency,
        type=transaction.type,
        category=transaction.category,
        transaction_date=transaction.date,
        receipt_name=transaction.receipt.name if transaction.receipt else "",
    )

    try:
        CloudFinancialPlatform().process_transaction(snapshot)
    except Exception as exc:
        logger.warning("Cloud sync skipped: %s", exc)
