from django.urls import path
from . import views

urlpatterns = [
    path('enquiry/', views.enquiry_list_create, name='enquiry_api'),
    # path('bankpincode/', views.bankpincode_list_create, name='bankpincode_api'),

     path('bank-interest/', views.bank_interest_list_create, name='bank_interest_api'),
]