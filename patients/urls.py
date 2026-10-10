from django.urls import path
from .views import (
    PatientMeProfileView,
    PatientDetailView,
    MedicalRecordListCreateView,
    MedicalRecordDetailView,
)

urlpatterns = [
    path('me/', PatientMeProfileView.as_view(), name='patient-me'),
    path('records/', MedicalRecordListCreateView.as_view(), name='patient-records'),
    path('records/<int:pk>/', MedicalRecordDetailView.as_view(), name='patient-record-detail'),
    path('<int:pk>/', PatientDetailView.as_view(), name='patient-detail'),
]
