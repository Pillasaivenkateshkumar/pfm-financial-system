from django import forms
from django.forms import ModelForm, DateInput
from .models import Transaction


class TransactionForm(ModelForm):

    date = forms.DateField(
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'placeholder': 'Select date',
            }
        ),
        help_text='Select date from calendar'
    )

    class Meta:
        model = Transaction
        fields = ['title', 'amount', 'type', 'category', 'date', 'receipt']

    def save(self, commit=True):
        transaction = super().save(commit=False)
        transaction.currency = 'EUR'
        if commit:
            transaction.save()
            self.save_m2m()
        return transaction
