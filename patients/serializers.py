from rest_framework import serializers
from .models import PatientProfile, MedicalRecordFile
from accounts.serializers import UserPublicSerializer


class MedicalRecordFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalRecordFile
        fields = ['id', 'patient', 'title', 'record_type', 'file', 'description', 'uploaded_at']
        read_only_fields = ['id', 'patient', 'uploaded_at']


class PatientProfileSerializer(serializers.ModelSerializer):
    user = UserPublicSerializer(read_only=True)
    records = MedicalRecordFileSerializer(many=True, read_only=True)

    class Meta:
        model = PatientProfile
        fields = [
            'id', 'user', 'blood_group', 'emergency_contact_name',
            'emergency_contact_phone', 'allergies', 'chronic_conditions',
            'medical_history_notes', 'records', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'records', 'created_at', 'updated_at']
