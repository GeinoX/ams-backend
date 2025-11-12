from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import StudentRegisterSerializer, CourseSerializer, TimetableSerializer, EnrollmentSerializer, MyTokenObtainPairSerializer, AttendanceCheckInSerializer, SessionSerializer, TeacherRegisterSerializer, SemesterSerializer
from .models import Course, Timetable, Enrollment, Attendance, Session, Student, PendingAttendance, Semester, Teacher, CourseAssignment
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CourseAssignmentSerializer
from rest_framework.permissions import AllowAny
from rest_framework import status, permissions
from django.utils import timezone
from .serializers import CourseStudentSerializer
from .utils import notify_session
from django.contrib.auth import logout

# Create your views here.

## Handles tokens, when this view is been called, it passes the data to the serializer
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
    
## Enables student to register
class StudentRegisterView(APIView):
    def post(self, request):
        serializer = StudentRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Student registered successfully"}, status=201)
        return Response(serializer.errors, status=400)


class TeacherRegisterView(APIView):
    def post(self, request):
        serializer = TeacherRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Teacher registered successfully"}, status=201)
        return Response(serializer.errors, status=400)


class StudentInfoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        ngrok_url = "https://e708f1bfee58.ngrok-free.app"

        try:
            student = Student.objects.get(user=user)
        except Student.DoesNotExist:
            return Response({'message': 'Student profile not found'}, status=status.HTTP_404_NOT_FOUND)

        return Response({
            'data': {
                'name': user.name,
                'program': student.program,
                "image": f"{ngrok_url}{user.profile_image.url}" if user.profile_image else None
            }
        }, status=status.HTTP_200_OK)


class TeacherInfoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        ngrok_url = "https://e708f1bfee58.ngrok-free.app"  # Replace with your actual media URL if needed

        try:
            teacher = Teacher.objects.get(user=user)
        except Teacher.DoesNotExist:
            return Response({'message': 'Teacher profile not found'}, status=status.HTTP_404_NOT_FOUND)

        return Response({
            'data': {
                'name': user.name,
                'department': teacher.department if hasattr(teacher, 'department') else None,
                "image": f"{ngrok_url}{user.profile_image.url}" if user.profile_image else None
            }
        }, status=status.HTTP_200_OK)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        if user.can_logout:
            return Response({"message": "Logged out successfully."}, status=200)
        else:
            return Response({"message": "You are not allowed to logout."}, status=403)




## Enables client view all courses, in the course page
class CourseView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        course = Course.objects.all()
        serializer = CourseSerializer(course, many=True)
        return Response(serializer.data)
    
## Enable client to view all courses filtered by level, in the course page
class CoursefilterView(APIView):
    permission_classes = [AllowAny]
    def get(self, request, level):
        course = Course.objects.filter(level=level)
        serializer = CourseSerializer(course, many=True)
        return Response(serializer.data)

## Handles the time timatable, enables didplay of the timetable in timetable page
class TimetableView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        try:
            # Get the Student linked to this user
            student = Student.objects.get(user=user)
        except Student.DoesNotExist:
            return Response({"error": "Student profile not found"}, status=404)

        # Get the current semester
        try:
            current_semester = Semester.objects.get(status="Current")
        except Semester.DoesNotExist:
            return Response({"error": "No current semester found"}, status=404)

        # Get enrollments only for that semester
        enrolled_courses = Enrollment.objects.filter(
            student=student,
            semester=current_semester
        ).values_list("course", flat=True)

        # Get timetable for those courses
        timetable = Timetable.objects.filter(course__in=enrolled_courses)

        serializer = TimetableSerializer(timetable, many=True)
        return Response(serializer.data)

    
class TeacherTimetableView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        try:
            # Get the Teacher object linked to this user
            teacher = Teacher.objects.get(user=user)
        except Teacher.DoesNotExist:
            return Response({"error": "Teacher profile not found"}, status=404)

        # Optional query parameters
        semester = request.query_params.get('semester')  # e.g., "Fall", "Summer"
        year = request.query_params.get('year')          # e.g., "2025"

        # Get courses assigned to this teacher, optionally filtering by semester/year
        assignments = CourseAssignment.objects.filter(teacher=teacher)
        if semester:
            assignments = assignments.filter(semester=semester)
        if year:
            assignments = assignments.filter(year=year)

        assigned_courses = assignments.values_list('course', flat=True)

        # Filter timetable for those courses
        timetable = Timetable.objects.filter(course__in=assigned_courses)

        serializer = TimetableSerializer(timetable, many=True)
        return Response(serializer.data)

## Handles student enrollment, enables students to enroll a course
class EnrollView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        course_name = request.data.get('course_name') 

        if not course_name:
            return Response({"error": "course_name is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            Course.objects.get(course_id=course_name)
        except Course.DoesNotExist:
            return Response({"error": "Course not found"}, status=status.HTTP_404_NOT_FOUND)

        # Prepare serializer with context
        serializer = EnrollmentSerializer(data=request.data, context={"request": request})

        if serializer.is_valid():
            serializer.save() 
            return Response({"message": "Enrollment successful"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetCurrentSemesterView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            latest_semester = Semester.objects.get(status="Current")
            serializer = SemesterSerializer(latest_semester)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Semester.DoesNotExist:
            return Response(
                {"error": "No current semester found."},
                status=status.HTTP_404_NOT_FOUND
            )





## View courses enrolled to in the attendance page and course page
class EnrollFilterView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request): #level
        student_profile = request.user.student_profile

        period = request.query_params.get('period')
        year = request.query_params.get('year')


        print(period)
        print(year)

        try:
            semester = Semester.objects.get(period=period, year=year, status="Current")
        except Semester.DoesNotExist:
                return Response({"error": "Semester not found or is not current"}, status=403)
        
        enrollments = Enrollment.objects.filter(student=student_profile, semester=semester) #course__level=level

        courses = [enrollment.course for enrollment in enrollments]

        # Serialize courses
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data)
    
class SessionView(APIView):
    def post(request):
        session = Session.objects.create(

        )
## Handles attendance 
class AttendanceCheckInView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AttendanceCheckInSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            session = serializer.context['session']
            student = request.user.student_profile
            added_students_ids = request.data.get("added_students", [])

            # Self check-in
            attendance, created = Attendance.objects.get_or_create(session=session, student=student)
            message = "Check-in successful!" if created else "Already checked in. Friend check-ins processed."

            # Friend check-ins (pending approval)
            for sid in added_students_ids:
                try:
                    friend = Student.objects.get(matricule=sid)
                    print(friend)
                    PendingAttendance.objects.get_or_create(
                        session=session,
                        adder=student,  
                        added_student=friend
                    )
                except Student.DoesNotExist:
                    continue  # skip invalid IDs

            return Response({"message": message}, status=201)

        return Response(serializer.errors, status=400)




## Enables teacher to start a session
class StartSessionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        # Ensure user is a teacher
        if not hasattr(request.user, 'teacher_profile'):
            return Response(
                {"error": "Only teachers can start a session."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = SessionSerializer(data=request.data)
        if serializer.is_valid():
            # Lookup the Course by name
            course_name = serializer.validated_data.get('course')
            print(course_name)
            try:
                course_obj = Course.objects.get(course_id=course_name)
                print(course_obj)
            except Course.DoesNotExist:
                return Response(
                    {"error": "Course does not exist."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Save session with proper foreign key
            session = Session.objects.create(
                teacher=request.user.teacher_profile,
                course=course_obj,
                active=True
            )

            return Response(
                SessionSerializer(session).data,
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


## Enables eacher to end a session
class StopSessionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, session_id):
        try:
            session = Session.objects.get(session_id=session_id, teacher=request.user.teacher_profile, active=True)
        except Session.DoesNotExist:
            return Response({"detail": "Session not found or already inactive."}, status=status.HTTP_404_NOT_FOUND)

        session.active = False
        session.end_time = timezone.now()
        session.save()
        return Response({"detail": "Session stopped successfully."}, status=status.HTTP_200_OK)
    

class StudentAttendanceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, course_id):
        student = request.user.student_profile

        # Get current semester
        current_semester = Semester.objects.filter(status="Current").first()
        if not current_semester:
            return Response({"error": "No current semester found"}, status=404)

        # Courses student is enrolled in this semester
        enrolled_courses = Enrollment.objects.filter(
            student=student,
            semester=current_semester
        ).values_list('course', flat=True)

        # Sessions for these courses
        all_sessions = Session.objects.filter(
            course__in=enrolled_courses,
            course__course_id__icontains=course_id
        ).order_by('start_time')

        student_attendance = Attendance.objects.filter(
            student=student,
            session__in=all_sessions
        )

        attended_ids = {a.session.session_id for a in student_attendance}

        result = []
        for i, session in enumerate(all_sessions, start=1):
            status = "Attended" if session.session_id in attended_ids else "Missed"
            result.append({
                "day": i,
                "session_id": session.session_id,
                "status": status
            })

        return Response(result)


## Enables teachers to get the courses assigned to them
class TeacherCoursesView(APIView):
    def get(self, request):
        # Ensure the user is a teacher
        if not hasattr(request.user, "teacher_profile"):
            return Response(
                {"error": "Only teachers can view assigned courses."},
                status=status.HTTP_403_FORBIDDEN
            )

        teacher = request.user.teacher_profile 
        year = request.query_params.get("year")
        semester = request.query_params.get("semester")

        # Validate required parameters
        if not (year and semester):
            return Response(
                {"error": "Both 'year' and 'semester' are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Query assignments for this teacher
        assignments = CourseAssignment.objects.filter(
            teacher=teacher,
            year=year,
            semester=semester
        ).select_related("teacher__user", "course")

        if not assignments.exists():
            return Response(
                {"message": "No courses found for this teacher in the specified year and semester."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Serialize and return data
        serializer = CourseAssignmentSerializer(assignments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# views.py (append)

class GetCourseStudentsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, course_id=None):
        """
        Retrieve all students enrolled in a course.
        Supports both path parameter and query parameter 'course_id' or 'course'.
        """

        #  Get course_id from path or query parameters
        course_id = course_id or request.query_params.get("course_id") or request.query_params.get("course")
        if not course_id:
            return Response(
                {"error": "course_id parameter is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        #  Restrict access to teachers/staff only
        if not hasattr(request.user, "teacher_profile") and not request.user.is_staff:
            return Response(
                {"error": "Only teachers or staff can view enrolled students."},
                status=status.HTTP_403_FORBIDDEN
            )

        #  Find the course
        try:
            course = Course.objects.get(course_id=course_id)
            print(course)
        except Course.DoesNotExist:
            return Response({"error": "Course not found."}, status=status.HTTP_404_NOT_FOUND)

        #  Query enrollments and related student info
        enrollments = Enrollment.objects.filter(course=course).select_related("student__user")
        print(enrollments)

        #  Pre-calc total sessions for this course
        total_sessions = Session.objects.filter(course=course).count()
        print(f"{total_sessions}")

        students_data = []
        for enrollment in enrollments:
            student = enrollment.student
            

            # Count attendance for this student
            attendance_qs = Attendance.objects.filter(session__course=course, student=student)
            attendance_count = attendance_qs.count()
            last_att = attendance_qs.order_by("-timestamp").first()
            last_att_ts = last_att.timestamp if last_att else None
            print(last_att_ts)

            students_data.append({
                "student_id": student.matricule,
                "name": getattr(student.user, "name", "") or getattr(student.user, "email", ""),
                "school_email": student.school_email,
                "attendance_count": attendance_count,
                "total_sessions": total_sessions,
                "last_attended": last_att_ts,
            })

        # 6️⃣ Serialize and return
        serializer = CourseStudentSerializer(students_data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class StudentAttView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, course_id=None):
        """
        Retrieve attendance details for the logged-in student in a specific course.
        """

        # Get course_id from path or query parameters
        course_id = course_id or request.query_params.get("course_id") or request.query_params.get("course")
        if not course_id:
            return Response(
                {"error": "course_id parameter is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Ensure user has a student profile
        if not hasattr(request.user, "student_profile"):
            return Response(
                {"error": "Only students can access this data."},
                status=status.HTTP_403_FORBIDDEN
            )

        student = request.user.student_profile

        # Find the course
        try:
            course = Course.objects.get(course_id=course_id)
        except Course.DoesNotExist:
            return Response({"error": "Course not found."}, status=status.HTTP_404_NOT_FOUND)

        # Check if the student is enrolled in this course
        if not Enrollment.objects.filter(student=student, course=course).exists():
            return Response({"error": "You are not enrolled in this course."}, status=status.HTTP_403_FORBIDDEN)

        # Count total sessions and attendance
        total_sessions = Session.objects.filter(course=course).count()
        attendance_qs = Attendance.objects.filter(session__course=course, student=student)
        attendance_count = attendance_qs.count()
        last_att = attendance_qs.order_by("-timestamp").first()
        last_att_ts = last_att.timestamp if last_att else None

        # Build response
        data = {
            "student_id": student.matricule,
            "name": getattr(student.user, "name", "") or getattr(student.user, "email", ""),
            "school_email": student.school_email,
            "attendance_count": attendance_count,
            "total_sessions": total_sessions,
            "last_attended": last_att_ts,
        }

        return Response(data, status=status.HTTP_200_OK)



class ReportDetectionView(APIView):
    def post(self, request):
        session_id = request.data.get("session_id")
        student_id = request.data.get("student_id")
        signal_strength = int(request.data.get("signal_strength", -100))
        added_students = request.data.get("added_students", [])

        # Low signal check
        if signal_strength < -70:
            notify_session(session_id, {
                "type": "low_signal",
                "student": {"id": student_id, "signal": signal_strength}
            })

        # If friends are added manually
        if added_students:
            notify_session(session_id, {
                "type": "manual_verification",
                "adder": {"id": student_id},
                "added": added_students
            })

        return Response({"status": "recorded"})
"""
class ApproveStudentsView(APIView):
    def post(self, request):
        session_id = request.data.get("session_id")
        students = request.data.get("students", [])
        session = Session.objects.get(session_id=session_id)

        for sid in students:
            Attendance.objects.filter(session=session, student_id=sid).update(status="present")

        return Response({"message": "Students approved successfully"})
"""
class ActiveSessionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        session_id = request.query_params.get("session_id")
        if not session_id:
            return Response(
                {"error": "session_id query parameter is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            
            session = Session.objects.get(session_id=session_id, active=True)
        except Session.DoesNotExist:
            return Response(
                {"error": "Active session not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Serialize and return session info
        serializer = SessionSerializer(session)
        return Response(serializer.data, status=status.HTTP_200_OK)

class PendingAttendanceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, session_id):
        # Ensure only teacher of session can view
        try:
            session = Session.objects.get(session_id=session_id, teacher=request.user.teacher_profile)
        except Session.DoesNotExist:
            return Response({"error": "Session not found or you are not the teacher."}, status=404)

        pending = PendingAttendance.objects.filter(session=session, approved=False).select_related('added_student', 'adder')
        result = [
            {
                "student_id": p.added_student.matricule,
                "student_name": p.added_student.user.name,
                "added_by_id": p.adder.matricule,
                "added_by_name": p.adder.user.name,
                "timestamp": p.timestamp
            } for p in pending
        ]
        return Response(result)
    

class ApprovePendingAttendanceView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        session_id = request.data.get("session_id")
        student_ids = request.data.get("student_ids", [])  # list of student matricules

        # Validate session & teacher
        try:
            session = Session.objects.get(session_id=session_id, teacher=request.user.teacher_profile)
        except Session.DoesNotExist:
            return Response({"error": "Session not found or you are not the teacher."}, status=404)

        # Track invalid IDs
        invalid_ids = []

        for sid in student_ids:
            try:
                # Fetch pending attendance for this student
                pending = PendingAttendance.objects.get(
                    session=session,
                    added_student__matricule=sid,
                    approved=False
                )
                
                # Add to attendance (or get existing)
                Attendance.objects.get_or_create(
                    session=session,
                    student=pending.added_student
                )

                # Mark as approved
                pending.approved = True
                pending.save()

            except PendingAttendance.DoesNotExist:
                invalid_ids.append(sid)  # collect IDs that don't match

        if invalid_ids:
            return Response(
                {"error": "Some student IDs are invalid or not pending."}, 
                status=400
            )  #"invalid_ids": invalid_ids 

        return Response({"message": "Selected students approved successfully."})

