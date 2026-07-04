from core.utils import get_enrollments, get_attendance

enrollments = get_enrollments()
Attendance  = get_attendance()



def mark_remaining_students_absent(session):
    students_enrolled = enrollments.filter(course_offering=session.course_offering)
    checkedin_students = Attendance.objects.filter(session=session)

    checkedin_students_ids = checkedin_students.values_list("student_id", flat=True)
    
    absent_students = students_enrolled.exclude(student_id__in =checkedin_students_ids)

    absences = []

    for enrollment in absent_students:
        absences.append(
            Attendance(
                student=enrollment.student,
                session=session,
                status="Absent"
            )
        )

    Attendance.objects.bulk_create(absences)



