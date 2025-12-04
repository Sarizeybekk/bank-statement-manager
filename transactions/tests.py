from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from datetime import date, timedelta
from decimal import Decimal
from .models import Transaction, ImportBatch
import io
import csv


class TransactionModelTest(TestCase):
    """Test Transaction model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_transaction_creation(self):
        """Test creating a transaction"""
        transaction = Transaction.objects.create(
            user=self.user,
            date=date.today(),
            amount=Decimal('1000.00'),
            currency='TRY',
            description='Test transaction',
            type='credit'
        )
        self.assertIsNotNone(transaction.unique_hash)
        self.assertEqual(transaction.user, self.user)
        self.assertEqual(transaction.amount, Decimal('1000.00'))


class TransactionUploadTest(TestCase):
    """Test CSV upload functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def create_csv_file(self, data):
        """Helper to create CSV file"""
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=['date', 'amount', 'currency', 'description', 'type'])
        writer.writeheader()
        writer.writerows(data)
        output.seek(0)
        return io.BytesIO(output.getvalue().encode('utf-8'))
    
    def test_upload_valid_csv(self):
        """Test uploading a valid CSV file"""
        csv_data = [
            {
                'date': '2025-07-01',
                'amount': '4500.00',
                'currency': 'TRY',
                'description': 'Satış: Fatura #1023',
                'type': 'credit'
            },
            {
                'date': '2025-07-02',
                'amount': '-1200.00',
                'currency': 'TRY',
                'description': 'Kira Ödemesi',
                'type': 'debit'
            }
        ]
        file = self.create_csv_file(csv_data)
        file.name = 'test.csv'
        
        url = reverse('upload-transactions')
        response = self.client.post(url, {'file': file}, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Transaction.objects.filter(user=self.user).count(), 2)
        self.assertEqual(response.data['imported_count'], 2)
    
    def test_upload_duplicate_idempotency_key(self):
        """Test idempotency key prevents duplicate uploads"""
        csv_data = [{
            'date': '2025-07-01',
            'amount': '1000.00',
            'currency': 'TRY',
            'description': 'Test',
            'type': 'credit'
        }]
        file = self.create_csv_file(csv_data)
        file.name = 'test.csv'
        
        url = reverse('upload-transactions')
        idempotency_key = 'test-key-123'
        
        # First upload
        response1 = self.client.post(
            url,
            {'file': file},
            format='multipart',
            HTTP_IDEMPOTENCY_KEY=idempotency_key
        )
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        
        # Second upload with same key
        file.seek(0)
        response2 = self.client.post(
            url,
            {'file': file},
            format='multipart',
            HTTP_IDEMPOTENCY_KEY=idempotency_key
        )
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)
        # Should return existing batch
        self.assertEqual(response2.data['batch']['id'], response1.data['batch']['id'])
    
    def test_upload_invalid_csv_format(self):
        """Test uploading invalid CSV format"""
        file = io.BytesIO(b'invalid csv content')
        file.name = 'test.csv'
        
        url = reverse('upload-transactions')
        response = self.client.post(url, {'file': file}, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TransactionListViewTest(TestCase):
    """Test transaction listing and filtering"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Create test transactions
        Transaction.objects.create(
            user=self.user,
            date=date.today(),
            amount=Decimal('1000.00'),
            currency='TRY',
            description='Credit transaction',
            type='credit',
            category='Sales'
        )
        Transaction.objects.create(
            user=self.user,
            date=date.today() - timedelta(days=1),
            amount=Decimal('500.00'),
            currency='TRY',
            description='Debit transaction',
            type='debit',
            category='Rent'
        )
    
    def test_list_transactions(self):
        """Test listing all transactions"""
        url = reverse('transaction-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_filter_by_type(self):
        """Test filtering transactions by type"""
        url = reverse('transaction-list')
        response = self.client.get(url, {'type': 'credit'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['type'], 'credit')
    
    def test_filter_by_date_range(self):
        """Test filtering transactions by date range"""
        url = reverse('transaction-list')
        start_date = (date.today() - timedelta(days=2)).strftime('%Y-%m-%d')
        end_date = date.today().strftime('%Y-%m-%d')
        
        response = self.client.get(url, {
            'start_date': start_date,
            'end_date': end_date
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)


class AuthenticationTest(TestCase):
    """Test authentication endpoints"""
    
    def setUp(self):
        self.client = APIClient()
    
    def test_register_user(self):
        """Test user registration"""
        url = reverse('register')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'testpass123',
            'password2': 'testpass123'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertTrue(User.objects.filter(username='newuser').exists())
    
    def test_login_user(self):
        """Test user login"""
        User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        url = reverse('login')
        data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        url = reverse('login')
        data = {
            'email': 'wrong@example.com',
            'password': 'wrongpass'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class KPIReportTest(TestCase):
    """Test KPI reporting endpoint"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Create test transactions
        Transaction.objects.create(
            user=self.user,
            date=date(2025, 7, 1),
            amount=Decimal('4500.00'),
            currency='TRY',
            description='Satış: Fatura #1023',
            type='credit',
            category='Sales'
        )
        Transaction.objects.create(
            user=self.user,
            date=date(2025, 7, 2),
            amount=Decimal('1200.00'),
            currency='TRY',
            description='Kira Ödemesi',
            type='debit',
            category='Rent'
        )
        Transaction.objects.create(
            user=self.user,
            date=date(2025, 7, 3),
            amount=Decimal('300.00'),
            currency='TRY',
            description='SaaS: CRM Aylık',
            type='debit',
            category='Software/Subscriptions'
        )
    
    def test_summary_report(self):
        """Test KPI summary report"""
        url = reverse('summary-report')
        response = self.client.get(url, {
            'start_date': '2025-07-01',
            'end_date': '2025-07-31'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_income'], 4500.0)
        self.assertEqual(response.data['total_expense'], 1500.0)
        self.assertEqual(response.data['net_cash_flow'], 3000.0)
        self.assertGreater(len(response.data['top_expense_categories']), 0)
    
    def test_summary_report_missing_dates(self):
        """Test summary report without required dates"""
        url = reverse('summary-report')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)



