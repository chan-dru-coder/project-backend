from django.urls import path
from .views import (
    AppointmentListCreateView,
    AppointmentDetailView,
    PrescriptionCreateView,
    PrescriptionDetailView,
    AppointmentDashboardStatsView,
)

urlpatterns = [
    path('', AppointmentListCreateView.as_view(), name='appointment-list-create'),
    path('stats/', AppointmentDashboardStatsView.as_view(), name='appointment-stats'),
    path('<uuid:pk>/', AppointmentDetailView.as_view(), name='appointment-detail'),
    path('<uuid:appointment_id>/prescription/', PrescriptionCreateView.as_view(), name='appointment-prescription-create'),
    path('<uuid:appointment_id>/prescription/detail/', PrescriptionDetailView.as_view(), name='appointment-prescription-detail'),
]
