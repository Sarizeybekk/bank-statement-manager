from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from transactions.models import Transaction
from .currency_converter import convert_currency, get_supported_currencies
from decimal import Decimal, InvalidOperation


@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter(
            'start_date',
            openapi.IN_QUERY,
            type=openapi.TYPE_STRING,
            format=openapi.FORMAT_DATE,
            required=True,
            description='Start date (YYYY-MM-DD)'
        ),
        openapi.Parameter(
            'end_date',
            openapi.IN_QUERY,
            type=openapi.TYPE_STRING,
            format=openapi.FORMAT_DATE,
            required=True,
            description='End date (YYYY-MM-DD)'
        ),
        openapi.Parameter(
            'target_currency',
            openapi.IN_QUERY,
            type=openapi.TYPE_STRING,
            required=False,
            description='Target currency code for conversion (e.g., USD, EUR, TRY). If not provided, amounts are returned in their original currencies.'
        ),
    ],
    responses={
        200: openapi.Response(
            'Summary report',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'total_income': openapi.Schema(type=openapi.TYPE_NUMBER),
                    'total_expense': openapi.Schema(type=openapi.TYPE_NUMBER),
                    'net_cash_flow': openapi.Schema(type=openapi.TYPE_NUMBER),
                    'currency': openapi.Schema(type=openapi.TYPE_STRING, description='Currency code for the amounts'),
                    'top_expense_categories': openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'category': openapi.Schema(type=openapi.TYPE_STRING),
                                'amount': openapi.Schema(type=openapi.TYPE_NUMBER),
                                'count': openapi.Schema(type=openapi.TYPE_INTEGER),
                            }
                        )
                    ),
                }
            )
        ),
        400: 'Bad Request',
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def summary_report(request):
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')
    
    if not start_date or not end_date:
        return Response(
            {'error': 'start_date and end_date are required (YYYY-MM-DD format)'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    except ValueError:
        return Response(
            {'error': 'Invalid date format. Use YYYY-MM-DD'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if start_date > end_date:
        return Response(
            {'error': 'start_date must be before or equal to end_date'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    target_currency = request.query_params.get('target_currency', '').upper().strip()
    if target_currency and target_currency not in get_supported_currencies():
        return Response(
            {'error': f'Unsupported currency: {target_currency}. Supported currencies: {", ".join(get_supported_currencies())}'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    transactions = Transaction.objects.filter(
        user=request.user,
        date__gte=start_date,
        date__lte=end_date
    )
    
    income_transactions = transactions.filter(type='credit')
    expense_transactions = transactions.filter(type='debit')
    
    income_by_currency = income_transactions.values('currency').annotate(total=Sum('amount'))
    expense_by_currency = expense_transactions.values('currency').annotate(total=Sum('amount'))
    
    if target_currency:
        total_income = Decimal('0')
        total_expense = Decimal('0')
        
        for item in income_by_currency:
            converted = convert_currency(
                item['total'],
                item['currency'],
                target_currency,
                date=str(end_date)
            )
            total_income += converted
        
        for item in expense_by_currency:
            converted = convert_currency(
                item['total'],
                item['currency'],
                target_currency,
                date=str(end_date)
            )
            total_expense += converted
        
        currency = target_currency
    else:
        total_income = sum(Decimal(str(item['total'])) for item in income_by_currency)
        total_expense = sum(Decimal(str(item['total'])) for item in expense_by_currency)
        currency = 'MIXED'
    
    net_cash_flow = total_income - total_expense
    
    top_expense_categories_raw = (
        expense_transactions
        .values('category', 'currency')
        .annotate(
            amount=Sum('amount'),
            count=Count('id')
        )
    )
    
    category_totals = {}
    for item in top_expense_categories_raw:
        category = item['category'] or 'Uncategorized'
        amount = Decimal(str(item['amount']))
        
        if target_currency:
            amount = convert_currency(
                amount,
                item['currency'],
                target_currency,
                date=str(end_date)
            )
        
        if category not in category_totals:
            category_totals[category] = {'amount': Decimal('0'), 'count': 0}
        
        category_totals[category]['amount'] += amount
        category_totals[category]['count'] += item['count']
    
    top_expense_categories = sorted(
        [
            {
                'category': cat,
                'amount': float(data['amount']),
                'count': data['count']
            }
            for cat, data in category_totals.items()
        ],
        key=lambda x: x['amount'],
        reverse=True
    )[:10]
    
    response_data = {
        'start_date': str(start_date),
        'end_date': str(end_date),
        'total_income': float(total_income),
        'total_expense': float(total_expense),
        'net_cash_flow': float(net_cash_flow),
        'currency': currency,
        'top_expense_categories': top_expense_categories
    }
    
    return Response(response_data, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter(
            'amount',
            openapi.IN_QUERY,
            type=openapi.TYPE_NUMBER,
            required=True,
            description='Amount to convert'
        ),
        openapi.Parameter(
            'from_currency',
            openapi.IN_QUERY,
            type=openapi.TYPE_STRING,
            required=True,
            description='Source currency code (e.g., USD, EUR, TRY)'
        ),
        openapi.Parameter(
            'to_currency',
            openapi.IN_QUERY,
            type=openapi.TYPE_STRING,
            required=True,
            description='Target currency code (e.g., USD, EUR, TRY)'
        ),
        openapi.Parameter(
            'date',
            openapi.IN_QUERY,
            type=openapi.TYPE_STRING,
            format=openapi.FORMAT_DATE,
            required=False,
            description='Date for historical exchange rate (YYYY-MM-DD). If not provided, uses latest rate.'
        ),
    ],
    responses={
        200: openapi.Response(
            'Currency conversion result',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'amount': openapi.Schema(type=openapi.TYPE_NUMBER),
                    'from_currency': openapi.Schema(type=openapi.TYPE_STRING),
                    'to_currency': openapi.Schema(type=openapi.TYPE_STRING),
                    'converted_amount': openapi.Schema(type=openapi.TYPE_NUMBER),
                    'exchange_rate': openapi.Schema(type=openapi.TYPE_NUMBER),
                    'date': openapi.Schema(type=openapi.TYPE_STRING),
                }
            )
        ),
        400: 'Bad Request',
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def convert_currency_endpoint(request):
    amount = request.query_params.get('amount')
    from_currency = request.query_params.get('from_currency', '').upper().strip()
    to_currency = request.query_params.get('to_currency', '').upper().strip()
    date = request.query_params.get('date')
    
    if not amount:
        return Response(
            {'error': 'amount parameter is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        amount = Decimal(str(amount))
    except (ValueError, InvalidOperation):
        return Response(
            {'error': 'Invalid amount format'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if not from_currency or not to_currency:
        return Response(
            {'error': 'from_currency and to_currency parameters are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    supported_currencies = get_supported_currencies()
    if from_currency not in supported_currencies:
        return Response(
            {'error': f'Unsupported source currency: {from_currency}. Supported: {", ".join(supported_currencies)}'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if to_currency not in supported_currencies:
        return Response(
            {'error': f'Unsupported target currency: {to_currency}. Supported: {", ".join(supported_currencies)}'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if date:
        try:
            datetime.strptime(date, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'Invalid date format. Use YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    from .currency_converter import get_exchange_rate
    exchange_rate = get_exchange_rate(from_currency, to_currency, date)
    
    converted_amount = convert_currency(amount, from_currency, to_currency, date)
    
    response_data = {
        'amount': float(amount),
        'from_currency': from_currency,
        'to_currency': to_currency,
        'converted_amount': float(converted_amount),
        'exchange_rate': float(exchange_rate),
        'date': date or 'latest'
    }
    
    return Response(response_data, status=status.HTTP_200_OK)



