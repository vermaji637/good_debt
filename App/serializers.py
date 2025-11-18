from rest_framework import serializers
from .models import Enquiry, BankPincode

class EnquirySerializer(serializers.ModelSerializer):
    class Meta:
        model = Enquiry
        fields = '__all__'


class BankPincodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankPincode
        fields = ['id', 'bank_name', 'pincode', 'city', 'state', 'bank_url', 'loan_types']


from .models import BankInterest
class BankInterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankInterest
        fields = "__all__"