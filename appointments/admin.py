from django.contrib import admin
from .models import Appointment, Prescription, PrescriptionItem


class PrescriptionItemInline(admin.TabularInline):
    model = PrescriptionItem
    extra = 1


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'doctor', 'appointment_date', 'appointment_time', 'meeting_type', 'status')
    list_filter = ('status', 'meeting_type', 'appointment_date')
    search_fields = ('patient__email', 'patient__first_name', 'doctor__user__email', 'doctor__user__last_name', 'reason_for_visit')
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'appointment', 'doctor', 'patient', 'follow_up_date', 'created_at')
    search_fields = ('patient__email', 'doctor__user__email', 'diagnosis')
    inlines = [PrescriptionItemInline]
    readonly_fields = ('id', 'created_at')
