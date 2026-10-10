from datetime import date, time, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from doctors.models import Specialization, DoctorProfile, AvailabilitySlot, DoctorReview
from patients.models import PatientProfile
from appointments.models import Appointment, Prescription, PrescriptionItem

User = get_user_model()


class Command(BaseCommand):
    help = 'Seeds database with realistic initial sample data for MediConnect'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Seeding MediConnect database..."))

        # 1. Create Superuser / Admin
        admin_email = "admin@meddiconnect.com"
        if not User.objects.filter(email=admin_email).exists():
            admin_user = User.objects.create_superuser(
                email=admin_email,
                password="admin123",
                first_name="MediConnect",
                last_name="Administrator"
            )
            self.stdout.write(self.style.SUCCESS(f"Created Superuser: {admin_email} (password: admin123)"))
        else:
            admin_user = User.objects.get(email=admin_email)

        # 2. Specializations
        specs_data = [
            ("Cardiology", "Heart, vascular, and circulatory health specialists.", "Heart"),
            ("Dermatology", "Expert skin, hair, and complex dermatological conditions.", "Sparkles"),
            ("Pediatrics", "Comprehensive healthcare for infants, children, and adolescents.", "Baby"),
            ("Neurology", "Disorders of the brain, spinal cord, and peripheral nerves.", "Brain"),
            ("General Medicine", "Primary healthcare consultations and preventive medical advice.", "Stethoscope"),
            ("Orthopedics", "Musculoskeletal system, bone fractures, and joint care.", "Activity"),
        ]
        specs = {}
        for name, desc, icon in specs_data:
            spec, _ = Specialization.objects.get_or_create(
                name=name,
                defaults={'description': desc, 'icon': icon}
            )
            specs[name] = spec
        self.stdout.write(self.style.SUCCESS(f"Loaded {len(specs)} Specializations"))

        # 3. Create Sample Doctors
        doctors_info = [
            {
                "email": "doctor.sarah@meddiconnect.com",
                "first_name": "Sarah",
                "last_name": "Johnson",
                "spec": "Cardiology",
                "hospital": "Metropolitan Heart Institute",
                "qualification": "MD, FACC (Cardiology)",
                "experience": 12,
                "fee": 90.00,
                "license": "MED-US-102938",
                "bio": "Dr. Sarah Johnson is a board-certified cardiologist with over a decade of clinical experience in preventive cardiovascular healthcare and hypertension management."
            },
            {
                "email": "doctor.marcus@meddiconnect.com",
                "first_name": "Marcus",
                "last_name": "Lee",
                "spec": "Dermatology",
                "hospital": "Downtown Skin & Aesthetic Clinic",
                "qualification": "MD, FAAD (Dermatology)",
                "experience": 8,
                "fee": 75.00,
                "license": "MED-US-203948",
                "bio": "Specialist in inflammatory skin diseases, acne management, and digital dermatoscopy."
            },
            {
                "email": "doctor.aisha@meddiconnect.com",
                "first_name": "Aisha",
                "last_name": "Patel",
                "spec": "Pediatrics",
                "hospital": "St. Jude Children's Wellness Hospital",
                "qualification": "MBBS, DCH, MD (Pediatrics)",
                "experience": 10,
                "fee": 65.00,
                "license": "MED-US-304958",
                "bio": "Compassionate pediatrician committed to holistic child growth tracking, immunizations, and adolescent medicine."
            },
            {
                "email": "doctor.david@meddiconnect.com",
                "first_name": "David",
                "last_name": "Chen",
                "spec": "Neurology",
                "hospital": "Central Neuro & Spine Center",
                "qualification": "MD, PhD (Neurology)",
                "experience": 15,
                "fee": 120.00,
                "license": "MED-US-405968",
                "bio": "Leading consultant neurologist focused on migraine management, neurodegenerative care, and neurological diagnostics."
            },
        ]

        created_doctors = []
        for doc in doctors_info:
            user, u_created = User.objects.get_or_create(
                email=doc["email"],
                defaults={
                    "first_name": doc["first_name"],
                    "last_name": doc["last_name"],
                    "role": User.Role.DOCTOR,
                    "phone_number": "+1-555-010-999"
                }
            )
            if u_created:
                user.set_password("doctor123")
                user.save()

            profile, _ = DoctorProfile.objects.get_or_create(user=user)
            profile.specialization = specs[doc["spec"]]
            profile.license_number = doc["license"]
            profile.hospital_name = doc["hospital"]
            profile.qualification = doc["qualification"]
            profile.experience_years = doc["experience"]
            profile.consultation_fee = doc["fee"]
            profile.bio = doc["bio"]
            profile.is_available = True
            profile.is_verified = True
            profile.save()
            created_doctors.append(profile)

            # Availability slots (Mon-Fri 09:00 - 13:00)
            for day in range(0, 5):
                AvailabilitySlot.objects.get_or_create(
                    doctor=profile,
                    day_of_week=day,
                    start_time=time(9, 0),
                    end_time=time(13, 0),
                    defaults={"slot_duration_minutes": 30, "is_active": True}
                )

        self.stdout.write(self.style.SUCCESS(f"Loaded {len(created_doctors)} Doctors and schedule slots (password: doctor123)"))

        # 4. Create Sample Patients
        patients_data = [
            {
                "email": "patient.alice@meddiconnect.com",
                "first_name": "Alice",
                "last_name": "Smith",
                "blood_group": "A+",
                "allergies": "Penicillin, Peanuts",
                "chronic": "None",
                "emergency_name": "John Smith",
                "emergency_phone": "+1-555-444-1111",
            },
            {
                "email": "patient.bob@meddiconnect.com",
                "first_name": "Bob",
                "last_name": "Miller",
                "blood_group": "O+",
                "allergies": "Sulfa drugs",
                "chronic": "Mild Hypertension",
                "emergency_name": "Emma Miller",
                "emergency_phone": "+1-555-444-2222",
            }
        ]

        created_patients = []
        for pdata in patients_data:
            user, p_created = User.objects.get_or_create(
                email=pdata["email"],
                defaults={
                    "first_name": pdata["first_name"],
                    "last_name": pdata["last_name"],
                    "role": User.Role.PATIENT,
                    "phone_number": "+1-555-888-3333"
                }
            )
            if p_created:
                user.set_password("patient123")
                user.save()

            profile, _ = PatientProfile.objects.get_or_create(user=user)
            profile.blood_group = pdata["blood_group"]
            profile.allergies = pdata["allergies"]
            profile.chronic_conditions = pdata["chronic"]
            profile.emergency_contact_name = pdata["emergency_name"]
            profile.emergency_contact_phone = pdata["emergency_phone"]
            profile.save()
            created_patients.append(user)

        self.stdout.write(self.style.SUCCESS(f"Loaded {len(created_patients)} Patients (password: patient123)"))

        # 5. Doctor Reviews
        DoctorReview.objects.get_or_create(
            doctor=created_doctors[0],
            patient=created_patients[0],
            defaults={
                "rating": 5,
                "review_text": "Dr. Sarah Johnson was exceptionally thorough and explained the cardiovascular tests in detail."
            }
        )
        DoctorReview.objects.get_or_create(
            doctor=created_doctors[1],
            patient=created_patients[1],
            defaults={
                "rating": 5,
                "review_text": "Great diagnosis and skin treatment plan. Significant improvement within a few days."
            }
        )

        # 6. Sample Appointments & Prescription
        today = timezone.now().date()
        apt1, _ = Appointment.objects.get_or_create(
            patient=created_patients[0],
            doctor=created_doctors[0],
            appointment_date=today + timedelta(days=2),
            appointment_time=time(10, 30),
            defaults={
                "meeting_type": Appointment.MeetingType.VIDEO_CALL,
                "status": Appointment.Status.CONFIRMED,
                "reason_for_visit": "Quarterly cardiology consultation",
                "symptoms": "Occasional palpitations during cardiovascular workouts"
            }
        )

        apt2, _ = Appointment.objects.get_or_create(
            patient=created_patients[1],
            doctor=created_doctors[1],
            appointment_date=today - timedelta(days=3),
            appointment_time=time(11, 0),
            defaults={
                "meeting_type": Appointment.MeetingType.IN_PERSON,
                "status": Appointment.Status.COMPLETED,
                "reason_for_visit": "Skin irritation and rash on arms",
                "symptoms": "Red itchy patches flare up after sun exposure"
            }
        )

        # Prescription for completed appointment
        if not hasattr(apt2, 'prescription'):
            prescription = Prescription.objects.create(
                appointment=apt2,
                doctor=apt2.doctor,
                patient=apt2.patient,
                diagnosis="Contact Dermatitis with mild secondary epidermal inflammation.",
                advice="Avoid direct sun exposure for 1 week. Use gentle soap and hydrate skin regularly.",
                follow_up_date=today + timedelta(days=14)
            )
            PrescriptionItem.objects.create(
                prescription=prescription,
                medicine_name="Hydrocortisone 1% Topical Cream",
                dosage="Thin layer",
                frequency="Twice daily",
                duration="7 days",
                instructions="Apply gently on clean affected areas after showering."
            )
            PrescriptionItem.objects.create(
                prescription=prescription,
                medicine_name="Cetirizine 10mg",
                dosage="1 tablet",
                frequency="Once daily at bedtime",
                duration="5 days",
                instructions="Take with water."
            )

        self.stdout.write(self.style.SUCCESS("Database seeding completed successfully!"))
