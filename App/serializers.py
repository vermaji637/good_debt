from rest_framework import serializers
from .models import Enquiry, BankPincode

class EnquirySerializer(serializers.ModelSerializer):
    class Meta:
        model = Enquiry
        fields = '__all__'

    # PAN validation
    def validate_pan_number(self, value):
        # Check length = 10
        if len(value) != 10:
            raise serializers.ValidationError("PAN number must be exactly 10 characters.")

        # Check uppercase
        if not value.isupper():
            raise serializers.ValidationError("PAN number must be in UPPERCASE.")

        return value

    # Convert PAN to uppercase before saving
    def create(self, validated_data):
        validated_data['pan_number'] = validated_data['pan_number'].upper()
        return super().create(validated_data)

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