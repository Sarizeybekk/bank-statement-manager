from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
import hashlib
import json


class ImportBatch(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='import_batches')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    filename = models.CharField(max_length=255)
    total_rows = models.IntegerField(default=0)
    imported_rows = models.IntegerField(default=0)
    failed_rows = models.IntegerField(default=0)
    idempotency_key = models.CharField(max_length=255, unique=True, null=True, blank=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"Batch {self.id} - {self.filename}"


class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('credit', 'Credit'),
        ('debit', 'Debit'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    date = models.DateField()
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    currency = models.CharField(max_length=3, default='TRY')
    description = models.TextField()
    type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    category = models.CharField(max_length=100, blank=True, null=True)
    unique_hash = models.CharField(max_length=64, unique=True, db_index=True)
    import_batch = models.ForeignKey(ImportBatch, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['user', 'date']),
            models.Index(fields=['user', 'type']),
            models.Index(fields=['user', 'category']),
        ]

    def __str__(self):
        return f"{self.date} - {self.amount} {self.currency} - {self.description[:50]}"

    @staticmethod
    def generate_unique_hash(user_id, date, amount, description, type):
        data = f"{user_id}_{date}_{amount}_{description}_{type}"
        return hashlib.sha256(data.encode()).hexdigest()

    def save(self, *args, **kwargs):
        if not self.unique_hash:
            self.unique_hash = self.generate_unique_hash(
                self.user.id,
                str(self.date),
                str(self.amount),
                self.description,
                self.type
            )
        super().save(*args, **kwargs)



