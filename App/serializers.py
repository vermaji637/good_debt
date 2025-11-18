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

        
    def get_bank_name(self, obj):
        enquiry = Enquiry.objects.filter(id=obj.enquiry_id).first()
        if not enquiry:
            return None
        
        bank = BankPincode.objects.filter(pincode=enquiry.current_pincode).first()
        return bank.bank_name if bank else None

    def get_pincode(self, obj):
        enquiry = Enquiry.objects.filter(id=obj.enquiry_id).first()
        return enquiry.current_pincode if enquiry else None