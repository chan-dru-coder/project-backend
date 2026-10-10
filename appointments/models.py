import uuid
from django.db import models
from django.conf import settings
from doctors.models import DoctorProfile


class Appointment(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        CONFIRMED = 'CONFIRMED', 'Confirmed'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        COMPLETED = 'COMPLETED', 'Completed'
        CANCELLED = 'CANCELLED', 'Cancelled'

    class MeetingType(models.TextChoices):
        IN_PERSON = 'IN_PERSON', 'In Person'
        VIDEO_CALL = 'VIDEO_CALL', 'Video Call'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='patient_appointments'
    )
    doctor = models.ForeignKey(
        DoctorProfile,
        on_delete=models.CASCADE,
        related_name='doctor_appointments'
    )
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    meeting_type = models.CharField(max_length=20, choices=MeetingType.choices, default=MeetingType.VIDEO_CALL)
    meeting_link = models.CharField(max_length=255, blank=True, help_text="Telehealth meeting room URL or code")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    reason_for_visit = models.CharField(max_length=255)
    symptoms = models.TextField(blank=True)
    cancellation_reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-appointment_date', '-appointment_time']
        indexes = [
            models.Index(fields=['appointment_date', 'status']),
            models.Index(fields=['patient', 'status']),
            models.Index(fields=['doctor', 'status']),
        ]

    def save(self, *args, **kwargs):
        if self.meeting_type == self.MeetingType.VIDEO_CALL and not self.meeting_link:
            self.meeting_link = f"https://meet.meddiconnect.health/room/{self.id}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Appointment on {self.appointment_date} {self.appointment_time} - Dr. {self.doctor.user.last_name} & {self.patient.email} [{self.status}]"


class Prescription(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    appointment = models.OneToOneField(
        Appointment,
        on_delete=models.CASCADE,
        related_name='prescription'
    )
    doctor = models.ForeignKey(
        DoctorProfile,
        on_delete=models.CASCADE,
        related_name='prescriptions_written'
    )
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='prescriptions'
    )
    diagnosis = models.TextField(help_text="Clinical diagnosis findings")
    advice = models.TextField(blank=True, help_text="Doctor advice, lifestyle, dietary recommendations")
    follow_up_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Prescription for {self.patient.email} by {self.doctor} ({self.created_at.strftime('%Y-%m-%d')})"


class PrescriptionItem(models.Model):
    prescription = models.ForeignKey(
        Prescription,
        on_delete=models.CASCADE,
        related_name='items'
    )
    medicine_name = models.CharField(max_length=150)
    dosage = models.CharField(max_length=80, help_text="e.g. 500mg, 1 tablet, 10ml")
    frequency = models.CharField(max_length=80, help_text="e.g. 1-0-1, Once daily, Twice a day")
    duration = models.CharField(max_length=80, help_text="e.g. 5 days, 2 weeks")
    instructions = models.CharField(max_length=255, blank=True, help_text="e.g. After food, At bedtime")

    def __str__(self):
        return f"{self.medicine_name} - {self.dosage} ({self.frequency})"
