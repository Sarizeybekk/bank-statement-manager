from django.contrib import admin
from .models import Transaction, ImportBatch


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('date', 'user', 'amount', 'currency', 'type', 'category', 'description')
    list_filter = ('type', 'currency', 'category', 'date')
    search_fields = ('description', 'user__username', 'user__email')
    readonly_fields = ('unique_hash', 'created_at')


@admin.register(ImportBatch)
class ImportBatchAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'filename', 'uploaded_at', 'total_rows', 'imported_rows', 'failed_rows')
    list_filter = ('uploaded_at',)
    search_fields = ('filename', 'user__username')



