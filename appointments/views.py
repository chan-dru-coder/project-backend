from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone

from .models import Appointment, Prescription
from .serializers import (
    AppointmentSerializer,
    AppointmentCreateSerializer,
    AppointmentStatusUpdateSerializer,
    PrescriptionSerializer,
)
from accounts.permissions import IsDoctor, IsPatient, IsDoctorOrAdmin


class AppointmentListCreateView(generics.ListCreateAPIView):
    """List user's appointments (Patient or Doctor) or create a new appointment booking."""
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'meeting_type', 'appointment_date']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AppointmentCreateSerializer
        return AppointmentSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == 'DOCTOR':
            return Appointment.objects.filter(doctor__user=user).select_related('patient', 'doctor__user', 'doctor__specialization')
        elif user.role == 'PATIENT':
            return Appointment.objects.filter(patient=user).select_related('patient', 'doctor__user', 'doctor__specialization')
        elif user.is_staff or user.role == 'ADMIN':
            return Appointment.objects.all().select_related('patient', 'doctor__user', 'doctor__specialization')
        return Appointment.objects.none()

    def perform_create(self, serializer):
        serializer.save(patient=self.request.user)


class AppointmentDetailView(generics.RetrieveUpdateAPIView):
    """View appointment details or update status (Confirm, Complete, Cancel)."""
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return AppointmentStatusUpdateSerializer
        return AppointmentSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == 'DOCTOR':
            return Appointment.objects.filter(doctor__user=user)
        elif user.role == 'PATIENT':
            return Appointment.objects.filter(patient=user)
        elif user.is_staff or user.role == 'ADMIN':
            return Appointment.objects.all()
        return Appointment.objects.none()


class PrescriptionCreateView(generics.CreateAPIView):
    """Doctor writes a prescription for a completed or confirmed appointment."""
    serializer_class = PrescriptionSerializer
    permission_classes = [IsDoctor]

    def perform_create(self, serializer):
        appointment_id = self.kwargs.get('appointment_id')
        appointment = get_object_or_404(
            Appointment,
            id=appointment_id,
            doctor__user=self.request.user
        )
        serializer.save(
            appointment=appointment,
            doctor=appointment.doctor,
            patient=appointment.patient
        )


class PrescriptionDetailView(generics.RetrieveAPIView):
    """Retrieve prescription details for an appointment."""
    serializer_class = PrescriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        appointment_id = self.kwargs.get('appointment_id')
        appointment = get_object_or_404(Appointment, id=appointment_id)

        # Ensure user is either the doctor or the patient or staff
        user = self.request.user
        if not (user == appointment.patient or user == appointment.doctor.user or user.is_staff or user.role == 'ADMIN'):
            self.permission_denied(self.request, message="You do not have permission to view this prescription.")

        return get_object_or_404(Prescription, appointment=appointment)


class AppointmentDashboardStatsView(APIView):
    """Returns appointment count metrics for user dashboard."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role == 'DOCTOR':
            qs = Appointment.objects.filter(doctor__user=user)
        elif user.role == 'PATIENT':
            qs = Appointment.objects.filter(patient=user)
        else:
            qs = Appointment.objects.all()

        today = timezone.now().date()
        stats = {
            'total': qs.count(),
            'pending': qs.filter(status='PENDING').count(),
            'confirmed': qs.filter(status='CONFIRMED').count(),
            'completed': qs.filter(status='COMPLETED').count(),
            'cancelled': qs.filter(status='CANCELLED').count(),
            'upcoming_today': qs.filter(appointment_date=today, status__in=['PENDING', 'CONFIRMED']).count(),
        }
        return Response(stats, status=status.HTTP_200_OK)
