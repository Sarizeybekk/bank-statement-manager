from rest_framework import serializers
from .models import Transaction, ImportBatch


class TransactionSerializer(serializers.ModelSerializer):
    converted_amount = serializers.SerializerMethodField()
    converted_currency = serializers.SerializerMethodField()
    
    class Meta:
        model = Transaction
        fields = ('id', 'date', 'amount', 'currency', 'converted_amount', 'converted_currency', 'description', 'type', 'category', 'created_at')
        read_only_fields = ('id', 'created_at', 'converted_amount', 'converted_currency')
    
    def get_converted_amount(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'target_currency') and request.target_currency:
            from reports.currency_converter import convert_currency
            try:
                return float(convert_currency(obj.amount, obj.currency, request.target_currency, date=str(obj.date)))
            except Exception:
                return None
        return None
    
    def get_converted_currency(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'target_currency') and request.target_currency:
            return request.target_currency
        return None


class ImportBatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImportBatch
        fields = ('id', 'uploaded_at', 'filename', 'total_rows', 'imported_rows', 'failed_rows')



