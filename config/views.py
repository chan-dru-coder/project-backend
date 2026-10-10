from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.db import connection
from django.utils import timezone


class HealthCheckView(APIView):
    """Health check endpoint verifying server, database connection and status."""
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        db_status = "healthy"
        db_details = ""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1;")
                cursor.fetchone()
                db_details = f"Connected to {connection.vendor} ({connection.settings_dict.get('NAME')})"
        except Exception as e:
            db_status = "unhealthy"
            db_details = str(e)

        overall_status = "ok" if db_status == "healthy" else "degraded"
        status_code = status.HTTP_200_OK if db_status == "healthy" else status.HTTP_503_SERVICE_UNAVAILABLE

        return Response(
            {
                "status": overall_status,
                "project": "MediConnect Backend API",
                "version": "1.0.0",
                "timestamp": timezone.now().isoformat(),
                "database": {
                    "status": db_status,
                    "engine": connection.settings_dict.get('ENGINE'),
                    "info": db_details,
                },
            },
            status=status_code
        )


class APIRootView(APIView):
    """API Root index view providing navigation to primary MediConnect endpoints."""
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response({
            "name": "MediConnect API",
            "version": "1.0.0",
            "description": "Comprehensive Telehealth & Healthcare Management Backend",
            "documentation": {
                "swagger_ui": request.build_absolute_uri('/api/docs/'),
                "redoc": request.build_absolute_uri('/api/redoc/'),
                "schema": request.build_absolute_uri('/api/schema/'),
            },
            "endpoints": {
                "health": request.build_absolute_uri('/api/health/'),
                "auth": {
                    "register": request.build_absolute_uri('/api/auth/register/'),
                    "login": request.build_absolute_uri('/api/auth/login/'),
                    "token_refresh": request.build_absolute_uri('/api/auth/token/refresh/'),
                    "profile": request.build_absolute_uri('/api/auth/profile/'),
                },
                "doctors": {
                    "list": request.build_absolute_uri('/api/doctors/'),
                    "me": request.build_absolute_uri('/api/doctors/me/'),
                    "specializations": request.build_absolute_uri('/api/doctors/specializations/'),
                    "slots": request.build_absolute_uri('/api/doctors/slots/'),
                },
                "patients": {
                    "me": request.build_absolute_uri('/api/patients/me/'),
                    "records": request.build_absolute_uri('/api/patients/records/'),
                },
                "appointments": {
                    "list_create": request.build_absolute_uri('/api/appointments/'),
                    "stats": request.build_absolute_uri('/api/appointments/stats/'),
                },
            }
        })
