from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from doctors.models import Specialization, DoctorProfile

User = get_user_model()


class DoctorsApiTests(APITestCase):
    def setUp(self):
        self.spec = Specialization.objects.create(
            name='Neurology',
            description='Nervous system treatments'
        )
        self.doc_user = User.objects.create_user(
            email='testdoc@meddiconnect.com',
            password='Password123!',
            first_name='Stephen',
            last_name='Strange',
            role=User.Role.DOCTOR
        )
        self.doc_profile = DoctorProfile.objects.get(user=self.doc_user)
        self.doc_profile.specialization = self.spec
        self.doc_profile.hospital_name = 'Metro General Hospital'
        self.doc_profile.consultation_fee = 100.00
        self.doc_profile.save()

    def test_list_specializations(self):
        url = reverse('specialization-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results'] if 'results' in response.data else response.data), 1)

    def test_list_doctors(self):
        url = reverse('doctor-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_doctor_detail(self):
        url = reverse('doctor-detail', kwargs={'pk': self.doc_profile.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['hospital_name'], 'Metro General Hospital')
