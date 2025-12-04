from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TransactionViewSet, upload_transactions

router = DefaultRouter()
router.register(r'', TransactionViewSet, basename='transaction')

urlpatterns = [
    path('upload/', upload_transactions, name='upload-transactions'),
    path('', include(router.urls)),
]



