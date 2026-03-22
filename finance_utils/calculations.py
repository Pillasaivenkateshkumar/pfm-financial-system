def total_income(transactions):
    return sum(t.amount for t in transactions if t.type == 'income')


def total_expense(transactions):
    return sum(t.amount for t in transactions if t.type == 'expense')


def balance(transactions):
    return total_income(transactions) - total_expense(transactions)