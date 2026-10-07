from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    message = "Administrator access required."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.is_staff
        )


class IsLecturer(BasePermission):
    message = "Lecturer access required."

    def has_permission(self, request, view):
        if not request.user:
            return False

        if not request.user.is_authenticated:
            return False

        try:
            request.user.lecturer_profile
        except Exception:
            return False

        return True


class MustNotChangePassword(BasePermission):
    message = (
        "You must change your temporary password "
        "before accessing this resource."
    )

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and not request.user.must_change_password
        )