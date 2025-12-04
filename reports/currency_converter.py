import requests
from decimal import Decimal, ROUND_DOWN
from django.core.cache import cache
from django.conf import settings


def get_exchange_rate(from_currency, to_currency, date=None):
    if from_currency.upper() == to_currency.upper():
        return Decimal('1.0')
    
    cache_key = f'exchange_rate_{from_currency}_{to_currency}_{date or "latest"}'
    try:
        cached_rate = cache.get(cache_key)
        if cached_rate:
            return Decimal(str(cached_rate))
    except Exception:
        pass
    
    try:
        if date:
            url = f'https://api.exchangerate-api.com/v4/historical/{from_currency.upper()}/{date}'
        else:
            url = f'https://api.exchangerate-api.com/v4/latest/{from_currency.upper()}'
        
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        if 'rates' in data:
            rate = Decimal(str(data['rates'].get(to_currency.upper(), 1)))
            try:
                cache.set(cache_key, float(rate), 3600)
            except Exception:
                pass
            return rate
        else:
            return Decimal('1.0')
            
    except (requests.RequestException, KeyError, ValueError) as e:
        print(f"Error fetching exchange rate: {e}")
        return Decimal('1.0')


def convert_currency(amount, from_currency, to_currency, date=None):
    if not amount:
        return Decimal('0.0')
    
    amount = Decimal(str(amount))
    rate = get_exchange_rate(from_currency, to_currency, date)
    converted = amount * rate
    
    return converted.quantize(Decimal('0.01'), rounding=ROUND_DOWN)


def get_supported_currencies():
    return [
        'TRY',
        'USD',
        'EUR',
        'GBP',
        'JPY',
        'CHF',
        'CAD',
        'AUD',
        'CNY',
        'RUB',
        'INR',
        'BRL',
        'ZAR',
        'MXN',
        'SGD',
        'HKD',
        'NOK',
        'SEK',
        'DKK',
        'PLN',
    ]

