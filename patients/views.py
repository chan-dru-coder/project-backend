from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import PatientProfile, MedicalRecordFile
from .serializers import PatientProfileSerializer, MedicalRecordFileSerializer
from accounts.permissions import IsPatient, IsDoctorOrAdmin


class PatientMeProfileView(generics.RetrieveUpdateAPIView):
    """Retrieve or update profile of current logged-in patient."""
    serializer_class = PatientProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        profile, _ = PatientProfile.objects.get_or_create(user=self.request.user)
        return profile


class PatientDetailView(generics.RetrieveAPIView):
    """Retrieve patient medical details (accessible by doctors and admins)."""
    queryset = PatientProfile.objects.select_related('user').prefetch_related('records').all()
    serializer_class = PatientProfileSerializer
    permission_classes = [IsDoctorOrAdmin]


class MedicalRecordListCreateView(generics.ListCreateAPIView):
    """List or upload medical record documents for the current patient."""
    serializer_class = MedicalRecordFileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role == 'PATIENT':
            return MedicalRecordFile.objects.filter(patient__user=self.request.user)
        elif self.request.user.role in ['DOCTOR', 'ADMIN']:
            patient_id = self.request.query_params.get('patient_id')
            if patient_id:
                return MedicalRecordFile.objects.filter(patient_id=patient_id)
        return MedicalRecordFile.objects.none()

    def perform_create(self, serializer):
        profile, _ = PatientProfile.objects.get_or_create(user=self.request.user)
        serializer.save(patient=profile)


class MedicalRecordDetailView(generics.RetrieveDestroyAPIView):
    """Retrieve or delete a specific medical document."""
    serializer_class = MedicalRecordFileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role in ['ADMIN', 'STAFF']:
            return MedicalRecordFile.objects.all()
        return MedicalRecordFile.objects.filter(patient__user=self.request.user)
