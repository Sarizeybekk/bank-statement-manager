import csv
import io
from decimal import Decimal, InvalidOperation
from datetime import datetime
from django.db import transaction as db_transaction
from .models import Transaction, ImportBatch


def categorize_transaction(description):
    description_lower = description.lower()
    
    if any(keyword in description_lower for keyword in ['satış', 'sale', 'invoice', 'fatura', 'ödeme alındı']):
        return 'Sales'
    
    if any(keyword in description_lower for keyword in ['kira', 'rent', 'mortgage']):
        return 'Rent'
    
    if any(keyword in description_lower for keyword in ['maaş', 'salary', 'personel', 'personnel']):
        return 'Salary'
    
    if any(keyword in description_lower for keyword in ['elektrik', 'electricity', 'su', 'water', 'gaz', 'gas', 'fatura', 'bill']):
        return 'Utilities'
    
    if any(keyword in description_lower for keyword in ['internet', 'telefon', 'phone', 'telecom']):
        return 'Telecommunications'
    
    if any(keyword in description_lower for keyword in ['saas', 'crm', 'software', 'yazılım', 'subscription']):
        return 'Software/Subscriptions'
    
    if any(keyword in description_lower for keyword in ['kırtasiye', 'stationery', 'ofis', 'office']):
        return 'Office Supplies'
    
    if any(keyword in description_lower for keyword in ['market', 'grocery', 'süpermarket']):
        return 'Groceries'
    
    if any(keyword in description_lower for keyword in ['yemek', 'restaurant', 'food']):
        return 'Food & Dining'
    
    if any(keyword in description_lower for keyword in ['ulaşım', 'transport', 'benzin', 'fuel', 'gas']):
        return 'Transportation'
    
    return 'Other'


def process_csv_file(file, user, idempotency_key=None):
    errors = []
    imported_count = 0
    failed_count = 0
    
    if idempotency_key:
        existing_batch = ImportBatch.objects.filter(idempotency_key=idempotency_key).first()
        if existing_batch:
            return existing_batch, existing_batch.imported_rows, existing_batch.failed_rows, []
    
    try:
        if hasattr(file, 'seek'):
            file.seek(0)
        content = file.read()
        if isinstance(content, bytes):
            content = content.decode('utf-8-sig')
        else:
            content = content.encode('utf-8').decode('utf-8-sig')
        if hasattr(file, 'seek'):
            file.seek(0)
    except Exception as e:
        errors.append(f"Error reading file: {str(e)}")
        return None, 0, 0, errors
    
    try:
        csv_reader = csv.DictReader(io.StringIO(content))
        rows = list(csv_reader)
        fieldnames = csv_reader.fieldnames
        if fieldnames:
            fieldnames = [field.strip().strip('\ufeff').strip() for field in fieldnames]
            csv_reader.fieldnames = fieldnames
    except Exception as e:
        errors.append(f"Error parsing CSV: {str(e)}")
        return None, 0, 0, errors
    
    required_columns = ['date', 'amount', 'currency', 'description', 'type']
    if not fieldnames or not all(col in fieldnames for col in required_columns):
        errors.append(f"Missing required columns. Expected: {', '.join(required_columns)}. Found: {', '.join(fieldnames or [])}")
        return None, 0, 0, errors
    
    batch = ImportBatch.objects.create(
        user=user,
        filename=file.name if hasattr(file, 'name') else 'uploaded_file.csv',
        total_rows=len(rows),
        idempotency_key=idempotency_key
    )
    
    try:
        with db_transaction.atomic():
            transactions_to_create = []
            
            for row_num, row in enumerate(rows, start=2):
                try:
                    row = {k.strip().strip('\ufeff').strip(): v for k, v in row.items() if k}
                    try:
                        date = datetime.strptime(row['date'].strip(), '%Y-%m-%d').date()
                    except ValueError:
                        errors.append(f"Row {row_num}: Invalid date format. Expected YYYY-MM-DD")
                        failed_count += 1
                        continue
                    
                    try:
                        amount = Decimal(str(row['amount']).strip())
                    except (InvalidOperation, ValueError):
                        errors.append(f"Row {row_num}: Invalid amount format")
                        failed_count += 1
                        continue
                    
                    transaction_type = row['type'].strip().lower()
                    if transaction_type not in ['credit', 'debit']:
                        errors.append(f"Row {row_num}: Invalid type. Must be 'credit' or 'debit'")
                        failed_count += 1
                        continue
                    
                    currency = row['currency'].strip().upper()
                    description = row['description'].strip()
                    
                    unique_hash = Transaction.generate_unique_hash(
                        user.id, str(date), str(amount),                         description, transaction_type
                    )
                    
                    if Transaction.objects.filter(unique_hash=unique_hash).exists():
                        failed_count += 1
                        continue
                    
                    category = categorize_transaction(description)
                    
                    transaction = Transaction(
                        user=user,
                        date=date,
                        amount=abs(amount),
                        currency=currency,
                        description=description,
                        type=transaction_type,
                        category=category,
                        unique_hash=unique_hash,
                        import_batch=batch
                    )
                    transactions_to_create.append(transaction)
                    imported_count += 1
                    
                except Exception as e:
                    errors.append(f"Row {row_num}: {str(e)}")
                    failed_count += 1
                    continue
            
            if transactions_to_create:
                Transaction.objects.bulk_create(transactions_to_create, ignore_conflicts=True)
            
            batch.imported_rows = imported_count
            batch.failed_rows = failed_count
            batch.save()
            
    except Exception as e:
        errors.append(f"Error during import: {str(e)}")
        failed_count = len(rows) - imported_count
    
    return batch, imported_count, failed_count, errors



