def get_enrollments():
    from courses.models import CourseEnrollment
    return CourseEnrollment.objects

def get_assignments():
    from courses.models import CourseAssignment
    return CourseAssignment.objects

def get_students():
    from auth_app.models import Student
    return Student.objects

def get_sessions():
    from class_sessions.models import Session
    return Session.objects

def get_enrollments():
    from courses.models import CourseEnrollment
    return CourseEnrollment.objects

def get_attendance():
    from attendance.models import Attendance
    return Attendance