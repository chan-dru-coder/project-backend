from rest_framework import serializers
from .models import Appointment, Prescription, PrescriptionItem
from accounts.serializers import UserPublicSerializer
from doctors.serializers import DoctorProfileSerializer
from doctors.models import DoctorProfile


class PrescriptionItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrescriptionItem
        fields = ['id', 'medicine_name', 'dosage', 'frequency', 'duration', 'instructions']


class PrescriptionSerializer(serializers.ModelSerializer):
    items = PrescriptionItemSerializer(many=True, required=False)
    doctor_name = serializers.CharField(source='doctor.user.get_full_name', read_only=True)
    patient_name = serializers.CharField(source='patient.get_full_name', read_only=True)

    class Meta:
        model = Prescription
        fields = [
            'id', 'appointment', 'doctor', 'doctor_name', 'patient',
            'patient_name', 'diagnosis', 'advice', 'follow_up_date',
            'items', 'created_at'
        ]
        read_only_fields = ['id', 'doctor', 'patient', 'created_at']

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        prescription = Prescription.objects.create(**validated_data)
        for item in items_data:
            PrescriptionItem.objects.create(prescription=prescription, **item)
        return prescription


class AppointmentSerializer(serializers.ModelSerializer):
    patient_info = UserPublicSerializer(source='patient', read_only=True)
    doctor_info = DoctorProfileSerializer(source='doctor', read_only=True)
    prescription = PrescriptionSerializer(read_only=True)

    class Meta:
        model = Appointment
        fields = [
            'id', 'patient', 'patient_info', 'doctor', 'doctor_info',
            'appointment_date', 'appointment_time', 'meeting_type',
            'meeting_link', 'status', 'reason_for_visit', 'symptoms',
            'cancellation_reason', 'prescription', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'patient', 'patient_info', 'doctor_info', 'meeting_link', 'prescription', 'created_at', 'updated_at']


class AppointmentCreateSerializer(serializers.ModelSerializer):
    doctor_id = serializers.PrimaryKeyRelatedField(
        queryset=DoctorProfile.objects.filter(is_available=True),
        source='doctor',
        write_only=True
    )

    class Meta:
        model = Appointment
        fields = [
            'id', 'doctor_id', 'appointment_date', 'appointment_time',
            'meeting_type', 'reason_for_visit', 'symptoms'
        ]
        read_only_fields = ['id']

    def validate(self, attrs):
        doctor = attrs.get('doctor')
        appointment_date = attrs.get('appointment_date')
        appointment_time = attrs.get('appointment_time')

        # Check for duplicate appointment with same doctor at same time
        clash = Appointment.objects.filter(
            doctor=doctor,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            status__in=['PENDING', 'CONFIRMED']
        ).exists()

        if clash:
            raise serializers.ValidationError("This doctor already has a booking at the selected date and time.")

        return attrs


class AppointmentStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ['status', 'cancellation_reason']

    def validate_status(self, value):
        allowed_transitions = ['CONFIRMED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED']
        if value not in allowed_transitions:
            raise serializers.ValidationError(f"Invalid status choice. Allowed: {allowed_transitions}")
        return value
