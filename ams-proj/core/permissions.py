from rest_framework.permissions import BasePermission
from .utils import get_enrollments, get_assignments, get_students, get_sessions

enrollments = get_enrollments()
assignments = get_assignments()
student = get_students()
sessions = get_sessions()

class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, 'student_profile')
    

class IsLecturer(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, 'lecturer_profile')
    
class IsEnrolled(BasePermission):
    def has_permission(self, request, view):
        added_students = request.data.get("added_students")
        session = request.data.get("session")
        user = request.user

        if not session:
            return False
        
        session_instance = sessions.select_related("course_offering").filter(session_id=session).first()

        if not session_instance:
            return False
        

        if not added_students:
            return enrollments.filter(student__user=user, course_offering=session_instance.course_offering).exists()
        
        if not enrollments.filter(student__user=user, course_offering=session_instance.course_offering).exists():
            return False
        
        for matricule in added_students:
            if not enrollments.filter(student__matricule=matricule, course_offering=session_instance.course_offering).exists():
                return False
        return True

            
class IsAssigned(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return assignments.filter(lecturer__user=user).exists()

class MustChangePassword(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated and request.user.must_change_password:
            return False  
        return True