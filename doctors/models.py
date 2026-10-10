from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.db.models import Avg


class Specialization(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, default='Stethoscope', help_text='Icon identifier')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class DoctorProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='doctor_profile'
    )
    specialization = models.ForeignKey(
        Specialization,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='doctors'
    )
    license_number = models.CharField(max_length=60, unique=True, blank=True, null=True)
    hospital_name = models.CharField(max_length=200, blank=True)
    qualification = models.CharField(max_length=200, blank=True, help_text="e.g. MBBS, MD, MS")
    experience_years = models.PositiveIntegerField(default=0)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    bio = models.TextField(blank=True)
    is_available = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-experience_years', '-created_at']

    def __str__(self):
        return f"Dr. {self.user.get_full_name() or self.user.email} - {self.specialization.name if self.specialization else 'General'}"

    @property
    def average_rating(self):
        agg = self.reviews.aggregate(avg=Avg('rating'))
        return round(agg['avg'], 1) if agg['avg'] is not None else 0.0

    @property
    def review_count(self):
        return self.reviews.count()


class AvailabilitySlot(models.Model):
    DAYS_OF_WEEK = (
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    )

    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='availability_slots')
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK)
    start_time = models.TimeField()
    end_time = models.TimeField()
    slot_duration_minutes = models.PositiveIntegerField(default=30)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['day_of_week', 'start_time']
        unique_together = ('doctor', 'day_of_week', 'start_time', 'end_time')

    def __str__(self):
        day_name = dict(self.DAYS_OF_WEEK).get(self.day_of_week, '')
        return f"{self.doctor} - {day_name} {self.start_time.strftime('%H:%M')} to {self.end_time.strftime('%H:%M')}"


class DoctorReview(models.Model):
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='reviews')
    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='doctor_reviews')
    rating = models.PositiveSmallIntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    review_text = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('doctor', 'patient')

    def __str__(self):
        return f"Review by {self.patient.email} for {self.doctor} ({self.rating}/5)"
