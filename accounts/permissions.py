from rest_framework import permissions


class IsPatient(permissions.BasePermission):
    """Allows access only to authenticated patients."""

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'PATIENT')


class IsDoctor(permissions.BasePermission):
    """Allows access only to authenticated doctors."""

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'DOCTOR')


class IsDoctorOrAdmin(permissions.BasePermission):
    """Allows access to doctors or staff/admins."""

    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated and (
                request.user.role in ['DOCTOR', 'ADMIN', 'STAFF'] or request.user.is_staff
            )
        )


class IsOwnerOrAdmin(permissions.BasePermission):
    """Object-level permission to only allow owners of an object to access or edit it."""

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff or request.user.role == 'ADMIN':
            return True
        if hasattr(obj, 'user'):
            return obj.user == request.user
        if hasattr(obj, 'patient'):
            return obj.patient == request.user or (hasattr(obj.patient, 'user') and obj.patient.user == request.user)
        return obj == request.user
