from django.urls import path
from .views import (
    SpecializationListView,
    DoctorListView,
    DoctorDetailView,
    DoctorMeProfileView,
    DoctorAvailabilitySlotListCreateView,
    DoctorAvailabilitySlotDetailView,
    DoctorReviewListCreateView,
)

urlpatterns = [
    path('', DoctorListView.as_view(), name='doctor-list'),
    path('me/', DoctorMeProfileView.as_view(), name='doctor-me'),
    path('specializations/', SpecializationListView.as_view(), name='specialization-list'),
    path('slots/', DoctorAvailabilitySlotListCreateView.as_view(), name='doctor-slots'),
    path('slots/<int:pk>/', DoctorAvailabilitySlotDetailView.as_view(), name='doctor-slot-detail'),
    path('<int:pk>/', DoctorDetailView.as_view(), name='doctor-detail'),
    path('<int:doctor_id>/reviews/', DoctorReviewListCreateView.as_view(), name='doctor-reviews'),
]
