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
        fields = ['title', 'currency', 'amount', 'type', 'category', 'date', 'receipt']