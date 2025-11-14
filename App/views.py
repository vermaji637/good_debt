from django.utils import timezone
from datetime import timedelta, date
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from App.models import Enquiry, BankPincode
from App.serializers import EnquirySerializer, BankPincodeSerializer


@api_view(['GET', 'POST'])
def enquiry_list_create(request):
    # ✅ GET — return all banks
    if request.method == 'GET':
        bank_data = BankPincode.objects.all()
        serializer = BankPincodeSerializer(bank_data, many=True)
        return Response(serializer.data)

    # ✅ POST — create a new enquiry
    elif request.method == 'POST':
        serializer = EnquirySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        # ✅ Age Validation
        dob = data['date_of_birth']
        today = date.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        if age < 23 or age > 60:
            return Response(
                {"message": "You are not eligible for the loan. Age must be between 23 and 60."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # ✅ Loan type validation
        loan_for = data.get('loan_for', '').lower()
        employee_type = data.get('employee_type')
        net_income = data.get('net_income')

        if loan_for == "personalloan" and not employee_type:
            return Response(
                {"message": "Employee type is mandatory for personal loan."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if loan_for == "businessloan" and not net_income:
            return Response(
                {"message": "Net income is mandatory for business loan."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # ✅ Check for duplicate enquiry within 3 days
        # phone_number = data['phone_number']
        # recent_enquiry = Enquiry.objects.filter(
        #     phone_number=phone_number,
        #     created_at__gte=timezone.now() - timedelta(days=3)
        # ).exists()

        # if recent_enquiry:
        #     return Response(
        #         {"message": "You already have an enquiry with this number. Please try again after 2–3 days."},
        #         status=status.HTTP_400_BAD_REQUEST
        #     )

        # ✅ Save enquiry
        enquiry = serializer.save()

        # ✅ Match bank by pincode
        # ✅ Match bank by pincode and loan type
        pincode = data['current_pincode']
        loan_for = data['loan_for'].lower()

# Map user input to our model loan types
        if loan_for == "personalloan":
          loan_filter = ['PL', 'BOTH']
        elif loan_for == "businessloan":
          loan_filter = ['BL', 'BOTH']
        else:
          loan_filter = ['BOTH']

        bank_data = BankPincode.objects.filter(pincode=pincode, loan_types__in=loan_filter)


        if not bank_data.exists():
            return Response(
                {
                    "message": "You are not eligible for any bank in this area. Please try another location.",
                    "enquiry_details": EnquirySerializer(enquiry).data,
                    "age": age,
                    "related_bank_details": []
                },
                status=status.HTTP_200_OK
            )

        bank_serializer = BankPincodeSerializer(bank_data, many=True)

        return Response(
            {
                "message": "Enquiry created successfully.",
                "enquiry_details": EnquirySerializer(enquiry).data,
                "age": age,
                "related_bank_details": bank_serializer.data
            },
            status=status.HTTP_201_CREATED
        )
