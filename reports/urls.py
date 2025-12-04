from django.urls import path
from . import views

urlpatterns = [
    path('summary/', views.summary_report, name='summary-report'),
    path('convert-currency/', views.convert_currency_endpoint, name='convert-currency'),
]



