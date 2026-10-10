from django.contrib import admin
from .models import PatientProfile, MedicalRecordFile


class MedicalRecordInline(admin.TabularInline):
    model = MedicalRecordFile
    extra = 1


@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'blood_group', 'emergency_contact_name', 'emergency_contact_phone', 'created_at')
    list_filter = ('blood_group', 'created_at')
    search_fields = ('user__first_name', 'user__last_name', 'user__email', 'emergency_contact_name')
    inlines = [MedicalRecordInline]


@admin.register(MedicalRecordFile)
class MedicalRecordFileAdmin(admin.ModelAdmin):
    list_display = ('title', 'patient', 'record_type', 'uploaded_at')
    list_filter = ('record_type', 'uploaded_at')
    search_fields = ('title', 'patient__user__email', 'description')
