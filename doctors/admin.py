from django.contrib import admin
from .models import Specialization, DoctorProfile, AvailabilitySlot, DoctorReview


@admin.register(Specialization)
class SpecializationAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'icon', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


class AvailabilitySlotInline(admin.TabularInline):
    model = AvailabilitySlot
    extra = 1


@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialization', 'hospital_name', 'consultation_fee', 'experience_years', 'is_available', 'is_verified')
    list_filter = ('is_available', 'is_verified', 'specialization')
    search_fields = ('user__first_name', 'user__last_name', 'user__email', 'hospital_name', 'license_number')
    inlines = [AvailabilitySlotInline]


@admin.register(DoctorReview)
class DoctorReviewAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'patient', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('doctor__user__email', 'patient__email', 'review_text')
