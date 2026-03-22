from django.db import models
from django.contrib.auth.models import User


# 🌍 Currency Options
CURRENCY_CHOICES = [
    ('INR', '₹ Indian Rupee'),
    ('USD', '$ US Dollar'),
    ('EUR', '€ Euro'),
    ('GBP', '£ British Pound'),
    ('AUD', 'A$ Australian Dollar'),
    ('CAD', 'C$ Canadian Dollar'),
    ('JPY', '¥ Japanese Yen'),
]


# 💰 Transaction Model
class Transaction(models.Model):

    TYPE_CHOICES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    title = models.CharField(max_length=200)

    # ⭐ Use Decimal for money
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    currency = models.CharField(
        max_length=3,
        choices=CURRENCY_CHOICES,
        default='INR'
    )

    type = models.CharField(
        max_length=10,
        choices=TYPE_CHOICES
    )

    category = models.CharField(max_length=100)

    date = models.DateField()

    # 📎 Optional receipt upload
    receipt = models.FileField(
        upload_to='receipts/',
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.title} - {self.amount} {self.currency}"


# 📊 Budget Model
class Budget(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    category = models.CharField(
        max_length=100,
        default="General"
    )

    # ⭐ Use Decimal for money
    limit = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    currency = models.CharField(
        max_length=3,
        choices=CURRENCY_CHOICES,
        default='INR'
    )

    # ⭐ Better month storage
    month = models.DateField(help_text="Use first day of month")

    def __str__(self):
        return f"{self.category} Budget - {self.limit} {self.currency}"