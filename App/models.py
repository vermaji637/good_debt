from django.db import models

class BankPincode(models.Model):
    LOAN_TYPE_CHOICES = [
        ('PL', 'Personal Loan'),
        ('BL', 'Business Loan'),
        ('BOTH', 'Both'),
    ]

    id = models.AutoField(primary_key=True)
    bank_name = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    bank_url = models.URLField(max_length=200)
    loan_types = models.CharField(max_length=10, choices=LOAN_TYPE_CHOICES, default='BOTH')

    def __str__(self):
        return f"{self.bank_name} ({self.loan_types})"


class Enquiry(models.Model):
    full_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15, unique=False)  # multiple after few days allowed
    email_address = models.EmailField(max_length=100)
    pan_number = models.CharField(max_length=10)
    date_of_birth = models.DateField()
    employee_type = models.CharField(max_length=50, blank=True, null=True)
    current_city = models.CharField(max_length=100)
    current_pincode = models.CharField(max_length=10)
    loan_for = models.CharField(max_length=100)
    net_income = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    departmentName = models.CharField(max_length=100, blank=True, null=True)
    designationName = models.CharField(max_length=100, blank=True, null=True)
    companyName = models.CharField(max_length=150, blank=True, null=True)
    
    designation = models.CharField(max_length=100, blank=True, null=True)
    departmentName = models.CharField(max_length=100, blank=True, null=True)
    companyName = models.CharField(max_length=150, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)  # for checking recent entries


    def save(self, *args, **kwargs):
        # Convert PAN number to uppercase before saving
        if self.pan_number:
            self.pan_number = self.pan_number.upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.full_name} - {self.loan_for}"



class BankInterest(models.Model):
    PROCESS_BY_CHOICES = (
        ("good_debt", "Good Debt"),
        ("bank", "Bank"),
    )

    bank_id = models.IntegerField()
    enquiry_id = models.IntegerField()
    process_by = models.CharField(max_length=20, choices=PROCESS_BY_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "bank_interest"   # <-- table name

    def __str__(self):
        return f"BankInterest {self.id}"