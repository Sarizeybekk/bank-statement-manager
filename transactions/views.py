from rest_framework import status, viewsets, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.conf import settings
from .models import Transaction, ImportBatch
from .serializers import TransactionSerializer, ImportBatchSerializer
from .utils import process_csv_file
from reports.currency_converter import get_supported_currencies


class TransactionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['type', 'currency']
    search_fields = ['description']
    ordering_fields = ['date', 'amount', 'created_at']
    ordering = ['-date']
    
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'target_currency',
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                required=False,
                description='Target currency code for conversion (e.g., USD, EUR, TRY). If provided, amounts will be converted to this currency.'
            ),
            openapi.Parameter(
                'start_date',
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE,
                required=False,
                description='Filter transactions from this date (YYYY-MM-DD)'
            ),
            openapi.Parameter(
                'end_date',
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE,
                required=False,
                description='Filter transactions until this date (YYYY-MM-DD)'
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        target_currency = request.query_params.get('target_currency', '').upper().strip()
        if target_currency:
            if target_currency not in get_supported_currencies():
                return Response(
                    {'error': f'Unsupported currency: {target_currency}. Supported currencies: {", ".join(get_supported_currencies())}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            request.target_currency = target_currency
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'target_currency',
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                required=False,
                description='Target currency code for conversion (e.g., USD, EUR, TRY). If provided, amounts will be converted to this currency.'
            ),
        ]
    )
    def retrieve(self, request, *args, **kwargs):
        target_currency = request.query_params.get('target_currency', '').upper().strip()
        if target_currency:
            if target_currency not in get_supported_currencies():
                return Response(
                    {'error': f'Unsupported currency: {target_currency}. Supported currencies: {", ".join(get_supported_currencies())}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            request.target_currency = target_currency
        return super().retrieve(request, *args, **kwargs)

    def get_queryset(self):
        queryset = Transaction.objects.filter(user=self.request.user)
        
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        
        category = self.request.query_params.get('category', '').strip()
        if category:
            queryset = queryset.filter(category__icontains=category)
        
        target_currency = self.request.query_params.get('target_currency', '').upper().strip()
        if target_currency:
            if target_currency not in get_supported_currencies():
                pass
            else:
                self.request.target_currency = target_currency
        
        return queryset
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class UploadTransactionsView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    @swagger_auto_schema(
        operation_description='Upload a CSV file containing bank transactions',
        manual_parameters=[
            openapi.Parameter(
                'file',
                openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                required=True,
                description='CSV file with transactions'
            ),
            openapi.Parameter(
                'Idempotency-Key',
                openapi.IN_HEADER,
                type=openapi.TYPE_STRING,
                required=False,
                description='Idempotency key to prevent duplicate uploads'
            ),
        ],
        responses={
            201: ImportBatchSerializer,
            400: 'Bad Request',
        }
    )
    def post(self, request):
        if 'file' not in request.FILES:
            return Response(
                {'error': 'No file provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        file = request.FILES['file']
        
        if not file.name.endswith('.csv'):
            return Response(
                {'error': 'File must be a CSV file'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        idempotency_key = request.headers.get('Idempotency-Key', None)
        
        try:
            batch, imported_count, failed_count, errors = process_csv_file(
                file, request.user, idempotency_key
            )
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"Error processing CSV: {error_trace}")
            error_message = f'Dosya işlenirken hata oluştu: {str(e)}'
            if settings.DEBUG:
                error_message += f' | Detay: {error_trace[:200]}'
            return Response(
                {'error': error_message, 'trace': error_trace if settings.DEBUG else None},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if batch is None:
            error_message = errors[0] if errors else 'Dosya işlenemedi'
            if len(errors) > 1:
                error_message += f' ({len(errors)} hata bulundu)'
            return Response(
                {'error': error_message, 'details': errors[:10] if len(errors) > 1 else errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        response_data = {
            'batch': ImportBatchSerializer(batch).data,
            'imported_count': imported_count,
            'failed_count': failed_count,
        }
        
        if errors:
            response_data['errors'] = errors[:10]
        
        if imported_count > 0:
            status_code = status.HTTP_201_CREATED
        elif failed_count > 0 and imported_count == 0:
            status_code = status.HTTP_200_OK
            response_data['message'] = 'No new transactions imported. All transactions may be duplicates or have errors.'
        else:
            status_code = status.HTTP_200_OK
            response_data['message'] = 'File processed but no transactions found.'
        
        return Response(response_data, status=status_code)


upload_transactions = UploadTransactionsView.as_view()

