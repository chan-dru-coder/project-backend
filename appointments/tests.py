from datetime import date, time, timedelta
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from doctors.models import Specialization, DoctorProfile
from appointments.models import Appointment

User = get_user_model()


class AppointmentsApiTests(APITestCase):
    def setUp(self):
        self.patient = User.objects.create_user(
            email='patient.test@meddiconnect.com',
            password='Password123!',
            first_name='Clara',
            last_name='Oswald',
            role=User.Role.PATIENT
        )
        self.doc_user = User.objects.create_user(
            email='doctor.test@meddiconnect.com',
            password='Password123!',
            first_name='Leonard',
            last_name='McCoy',
            role=User.Role.DOCTOR
        )
        self.spec = Specialization.objects.create(name='General Practice')
        self.doctor_profile = DoctorProfile.objects.get(user=self.doc_user)
        self.doctor_profile.specialization = self.spec
        self.doctor_profile.save()

    def test_create_and_list_appointment(self):
        self.client.force_authenticate(user=self.patient)
        url = reverse('appointment-list-create')
        future_date = date.today() + timedelta(days=5)
        payload = {
            'doctor_id': self.doctor_profile.id,
            'appointment_date': future_date.isoformat(),
            'appointment_time': '10:00:00',
            'meeting_type': 'VIDEO_CALL',
            'reason_for_visit': 'Annual routine checkup',
            'symptoms': 'None'
        }
        create_res = self.client.post(url, payload)
        self.assertEqual(create_res.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', create_res.data)

        # Check list endpoint
        list_res = self.client.get(url)
        self.assertEqual(list_res.status_code, status.HTTP_200_OK)
