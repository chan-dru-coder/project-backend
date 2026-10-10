from rest_framework import serializers
from .models import Specialization, DoctorProfile, AvailabilitySlot, DoctorReview
from accounts.serializers import UserPublicSerializer


class SpecializationSerializer(serializers.ModelSerializer):
    doctor_count = serializers.IntegerField(source='doctors.count', read_only=True)

    class Meta:
        model = Specialization
        fields = ['id', 'name', 'slug', 'description', 'icon', 'doctor_count', 'created_at']
        read_only_fields = ['id', 'slug', 'doctor_count', 'created_at']


class AvailabilitySlotSerializer(serializers.ModelSerializer):
    day_name = serializers.CharField(source='get_day_of_week_display', read_only=True)

    class Meta:
        model = AvailabilitySlot
        fields = ['id', 'doctor', 'day_of_week', 'day_name', 'start_time', 'end_time', 'slot_duration_minutes', 'is_active']
        read_only_fields = ['id', 'doctor']


class DoctorReviewSerializer(serializers.ModelSerializer):
    patient_info = UserPublicSerializer(source='patient', read_only=True)

    class Meta:
        model = DoctorReview
        fields = ['id', 'doctor', 'patient', 'patient_info', 'rating', 'review_text', 'created_at']
        read_only_fields = ['id', 'doctor', 'patient', 'patient_info', 'created_at']


class DoctorProfileSerializer(serializers.ModelSerializer):
    user = UserPublicSerializer(read_only=True)
    specialization_detail = SpecializationSerializer(source='specialization', read_only=True)
    specialization_id = serializers.PrimaryKeyRelatedField(
        queryset=Specialization.objects.all(),
        source='specialization',
        write_only=True,
        required=False,
        allow_null=True
    )
    average_rating = serializers.FloatField(read_only=True)
    review_count = serializers.IntegerField(read_only=True)
    availability_slots = AvailabilitySlotSerializer(many=True, read_only=True)

    class Meta:
        model = DoctorProfile
        fields = [
            'id', 'user', 'specialization', 'specialization_id', 'specialization_detail',
            'license_number', 'hospital_name', 'qualification', 'experience_years',
            'consultation_fee', 'bio', 'is_available', 'is_verified',
            'average_rating', 'review_count', 'availability_slots',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'is_verified', 'average_rating', 'review_count', 'created_at', 'updated_at']
