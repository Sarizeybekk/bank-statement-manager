from celery import shared_task
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings
from transactions.models import Transaction
from django.db.models import Sum, Count


@shared_task
def send_weekly_report():
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=7)
    
    users = User.objects.all()
    
    for user in users:
        transactions = Transaction.objects.filter(
            user=user,
            date__gte=start_date,
            date__lte=end_date
        )
        
        total_income = transactions.filter(type='credit').aggregate(total=Sum('amount'))['total'] or 0
        total_expense = transactions.filter(type='debit').aggregate(total=Sum('amount'))['total'] or 0
        net_cash_flow = total_income - total_expense
        
        print(f"Weekly report for {user.email}: Income={total_income}, Expense={total_expense}, Net={net_cash_flow}")
    
    return f"Sent weekly reports to {users.count()} users"



