# 🏥 MediConnect Backend API

> Robust, secure, and production-ready healthcare and telehealth platform backend built with **Django REST Framework** and **PostgreSQL**.

---

## 🌟 Features

- **Authentication & Role-Based Access Control**:
  - Custom User model supporting **Patients**, **Doctors**, **Admins**, and **Staff**.
  - Secure JWT authentication (`access` & `refresh` tokens) via `djangorestframework-simplejwt`.
  - Self-service registration and profile management.
- **Doctor & Specialty Directory**:
  - Medical specializations (Cardiology, Dermatology, Pediatrics, Neurology, etc.).
  - Doctor profiles with hospital affiliation, qualifications, fees, experience, and verified status.
  - Doctor availability schedules and time slots.
  - Patient ratings and clinical reviews.
- **Patient Health Records**:
  - Comprehensive health profiles: blood groups, allergies, chronic illnesses, emergency contacts.
  - Medical file attachments (lab reports, prescriptions, scans, discharge summaries).
- **Appointment & Telehealth Booking**:
  - In-person and video consultations with automated meeting room generation.
  - Complete lifecycle management (`PENDING`, `CONFIRMED`, `IN_PROGRESS`, `COMPLETED`, `CANCELLED`).
  - Electronic medical prescriptions with itemized dosages, frequencies, and instructions.
- **Developer Experience**:
  - Interactive OpenAPI / Swagger UI (`/api/docs/`) and ReDoc (`/api/redoc/`).
  - Automated database seeding (`python manage.py seed_data`).
  - Dedicated `/api/health/` monitoring endpoint.
  - Full CORS integration for React, Next.js, Vue, and Vite frontends.

---

## 🛠️ Technology Stack

| Component | Technology |
|---|---|
| **Framework** | Django 6+ / Django REST Framework |
| **Database** | PostgreSQL 14+ (Driver: `psycopg` 3.x) |
| **Authentication** | JSON Web Tokens (`djangorestframework-simplejwt`) |
| **API Docs** | OpenAPI 3.0 via `drf-spectacular` (Swagger & ReDoc) |
| **Configuration** | `python-dotenv` |
| **Media & Images** | Pillow |

---

## 🚀 Quickstart Guide

### 1. Prerequisites
- Python 3.10+
- PostgreSQL 14+ running locally or in Docker

### 2. Environment Configuration
Copy `.env.example` to `.env` (already configured if running locally):
```env
SECRET_KEY=your-secure-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_ENGINE=django.db.backends.postgresql
DB_NAME=meddiconnect_db
DB_USER=postgres
DB_PASSWORD=root
DB_HOST=localhost
DB_PORT=5432

CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
CORS_ALLOW_ALL_ORIGINS=True
```

### 3. Activate Virtual Environment & Install Dependencies
```powershell
# Windows
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 4. Run Database Migrations
```powershell
python manage.py migrate
```

### 5. Seed Test Data (Recommended)
Populate doctors, specializations, patients, sample appointments, and admin credentials:
```powershell
python manage.py seed_data
```

### 6. Start Development Server
```powershell
python manage.py runserver
```
The server will start at: `http://127.0.0.1:8000/`

---

## 🔑 Pre-seeded Demo Accounts

| Role | Email | Password | Details |
|---|---|---|---|
| **Super Admin** | `admin@meddiconnect.com` | `admin123` | Full Django admin & API permissions |
| **Doctor (Cardiology)** | `doctor.sarah@meddiconnect.com` | `doctor123` | Dr. Sarah Johnson (12 yrs exp, $90/visit) |
| **Doctor (Dermatology)** | `doctor.marcus@meddiconnect.com` | `doctor123` | Dr. Marcus Lee (8 yrs exp, $75/visit) |
| **Doctor (Pediatrics)** | `doctor.aisha@meddiconnect.com` | `doctor123` | Dr. Aisha Patel (10 yrs exp, $65/visit) |
| **Patient 1** | `patient.alice@meddiconnect.com` | `patient123` | Alice Smith (A+ blood, allergies) |
| **Patient 2** | `patient.bob@meddiconnect.com` | `patient123` | Bob Miller (O+ blood, Hypertension) |

---

## 📖 API Documentation & Endpoints

Interactive documentation is available when running the server:
- **Swagger UI**: [http://127.0.0.1:8000/api/docs/](http://127.0.0.1:8000/api/docs/)
- **ReDoc**: [http://127.0.0.1:8000/api/redoc/](http://127.0.0.1:8000/api/redoc/)
- **OpenAPI Schema (JSON/YAML)**: [http://127.0.0.1:8000/api/schema/](http://127.0.0.1:8000/api/schema/)

### Core Endpoint Summary

#### 1. System & Authentication (`/api/auth/`)
| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/api/health/` | Service & PostgreSQL health check | No |
| `POST` | `/api/auth/register/` | Register patient or doctor (returns JWT) | No |
| `POST` | `/api/auth/login/` | Obtain JWT tokens & user metadata | No |
| `POST` | `/api/auth/token/refresh/` | Refresh JWT access token | No |
| `GET/PUT/PATCH` | `/api/auth/profile/` | Current user profile | Bearer Token |
| `POST` | `/api/auth/change-password/` | Change account password | Bearer Token |

#### 2. Doctors (`/api/doctors/`)
| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/api/doctors/` | Search/filter doctors (`?specialization=&is_available=`) | No |
| `GET` | `/api/doctors/<id>/` | View doctor profile & availability slots | No |
| `GET/PUT` | `/api/doctors/me/` | Update logged-in doctor's clinical profile | Doctor |
| `GET` | `/api/doctors/specializations/` | List medical specialties | No |
| `GET/POST` | `/api/doctors/slots/` | View or create doctor availability slots | Doctor |
| `GET/POST` | `/api/doctors/<id>/reviews/`| View reviews or submit a rating | Patient |

#### 3. Patients (`/api/patients/`)
| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET/PUT/PATCH` | `/api/patients/me/` | View & update medical profile | Authenticated |
| `GET` | `/api/patients/<id>/` | View patient profile (for doctors/admin) | Doctor / Admin |
| `GET/POST` | `/api/patients/records/` | List or upload medical files (lab reports, scans) | Authenticated |
| `GET/DELETE` | `/api/patients/records/<id>/`| View or delete medical file | Authenticated |

#### 4. Appointments & Telehealth (`/api/appointments/`)
| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/api/appointments/` | List appointments (doctor or patient scoped) | Bearer Token |
| `POST` | `/api/appointments/` | Book an appointment with a doctor | Patient |
| `GET/PATCH` | `/api/appointments/<uuid>/` | View details or update status | Bearer Token |
| `GET` | `/api/appointments/stats/` | Dashboard metrics (upcoming, completed, etc.) | Bearer Token |
| `POST` | `/api/appointments/<uuid>/prescription/` | Doctor writes prescription with medications | Doctor |
| `GET` | `/api/appointments/<uuid>/prescription/detail/` | View prescription & medication instructions | Doctor/Patient |

---

## 🧪 Running Automated Tests

```powershell
python manage.py test
```

All test suites cover authentication, role validation, doctor catalog, appointment scheduling, and database connectivity.
