from django.db import models
from django.conf import settings


class PatientProfile(models.Model):
    class BloodGroup(models.TextChoices):
        A_POS = 'A+', 'A+'
        A_NEG = 'A-', 'A-'
        B_POS = 'B+', 'B+'
        B_NEG = 'B-', 'B-'
        AB_POS = 'AB+', 'AB+'
        AB_NEG = 'AB-', 'AB-'
        O_POS = 'O+', 'O+'
        O_NEG = 'O-', 'O-'
        UNKNOWN = 'UNKNOWN', 'Unknown'

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='patient_profile'
    )
    blood_group = models.CharField(max_length=10, choices=BloodGroup.choices, default=BloodGroup.UNKNOWN)
    emergency_contact_name = models.CharField(max_length=120, blank=True)
    emergency_contact_phone = models.CharField(max_length=25, blank=True)
    allergies = models.TextField(blank=True, help_text="Known medication/food allergies")
    chronic_conditions = models.TextField(blank=True, help_text="e.g. Asthma, Hypertension, Diabetes")
    medical_history_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Patient: {self.user.get_full_name() or self.user.email} ({self.blood_group})"


class MedicalRecordFile(models.Model):
    class RecordType(models.TextChoices):
        LAB_REPORT = 'LAB_REPORT', 'Lab Report'
        PRESCRIPTION = 'PRESCRIPTION', 'Prescription'
        IMAGING = 'IMAGING', 'Imaging / X-Ray / MRI'
        DISCHARGE_SUMMARY = 'DISCHARGE_SUMMARY', 'Discharge Summary'
        OTHER = 'OTHER', 'Other'

    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='records')
    title = models.CharField(max_length=200)
    record_type = models.CharField(max_length=30, choices=RecordType.choices, default=RecordType.OTHER)
    file = models.FileField(upload_to='patient_records/%Y/%m/')
    description = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.title} - {self.patient.user.email} ({self.record_type})"
