from rest_framework import generics, permissions, status, filters
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404

from .models import Specialization, DoctorProfile, AvailabilitySlot, DoctorReview
from .serializers import (
    SpecializationSerializer,
    DoctorProfileSerializer,
    AvailabilitySlotSerializer,
    DoctorReviewSerializer,
)
from accounts.permissions import IsDoctor, IsPatient, IsDoctorOrAdmin


class SpecializationListView(generics.ListCreateAPIView):
    """List all medical specializations or create a new one (staff/admin)."""
    queryset = Specialization.objects.all()
    serializer_class = SpecializationSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]


class DoctorListView(generics.ListAPIView):
    """Search and filter doctors by specialization, name, or availability."""
    queryset = DoctorProfile.objects.select_related('user', 'specialization').prefetch_related('reviews').all()
    serializer_class = DoctorProfileSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['specialization', 'is_available', 'is_verified']
    search_fields = ['user__first_name', 'user__last_name', 'hospital_name', 'specialization__name', 'qualification']
    ordering_fields = ['consultation_fee', 'experience_years', 'created_at']


class DoctorDetailView(generics.RetrieveAPIView):
    """Retrieve full details of a specific doctor."""
    queryset = DoctorProfile.objects.select_related('user', 'specialization').prefetch_related('reviews', 'availability_slots').all()
    serializer_class = DoctorProfileSerializer
    permission_classes = [permissions.AllowAny]


class DoctorMeProfileView(generics.RetrieveUpdateAPIView):
    """Retrieve or update current authenticated doctor's profile."""
    serializer_class = DoctorProfileSerializer
    permission_classes = [IsDoctor]

    def get_object(self):
        profile, _ = DoctorProfile.objects.get_or_create(user=self.request.user)
        return profile


class DoctorAvailabilitySlotListCreateView(generics.ListCreateAPIView):
    """List or create availability slots for the logged-in doctor."""
    serializer_class = AvailabilitySlotSerializer
    permission_classes = [IsDoctor]

    def get_queryset(self):
        return AvailabilitySlot.objects.filter(doctor__user=self.request.user)

    def perform_create(self, serializer):
        doctor_profile = get_object_or_404(DoctorProfile, user=self.request.user)
        serializer.save(doctor=doctor_profile)


class DoctorAvailabilitySlotDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Manage a specific availability slot."""
    serializer_class = AvailabilitySlotSerializer
    permission_classes = [IsDoctor]

    def get_queryset(self):
        return AvailabilitySlot.objects.filter(doctor__user=self.request.user)


class DoctorReviewListCreateView(generics.ListCreateAPIView):
    """List reviews for a doctor or post a new review (Patient only)."""
    serializer_class = DoctorReviewSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsPatient()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        doctor_id = self.kwargs.get('doctor_id')
        return DoctorReview.objects.filter(doctor_id=doctor_id)

    def perform_create(self, serializer):
        doctor_id = self.kwargs.get('doctor_id')
        doctor = get_object_or_404(DoctorProfile, id=doctor_id)
        serializer.save(doctor=doctor, patient=self.request.user)
