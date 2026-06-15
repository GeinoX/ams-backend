from django.shortcuts import get_object_or_404
from django.db.models import Count, Max
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import (
    StudentRegisterSerializer,
    MyTokenObtainPairSerializer,
    TeacherRegisterSerializer,
    CourseSerializer,
    EnrollmentCreateSerializer,
    EnrollmentViewSerializer,
    CourseOfferingSerializer,
    AttendanceCheckInSerializer,
    CourseAttendanceStatsSerializer,
    StudentSessionAttendanceSerializer,
    StudentAttendanceSummarySerializer,
    LecturerCourseAssignmentSerializer,
    SessionSerializer,
    PendingAttendanceSerializer,
)
from .models import (
    Student, Teacher, CourseOffering, Enrollment, Course,
    Attendance, PendingAttendance, Semester, Session, CourseAssignment,
)


# ==============================
# Auth
# ==============================
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class StudentRegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = StudentRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            response_data = StudentRegisterSerializer(user).data
            return Response(
                {"message": "Student registered successfully", "user": response_data},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TeacherRegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = TeacherRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            response_data = TeacherRegisterSerializer(user).data
            return Response(
                {"message": "Teacher registered successfully", "user": response_data},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ==============================
# Profile Info
# ==============================
class StudentInfoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        try:
            student = Student.objects.get(user=user)
        except Student.DoesNotExist:
            return Response({'message': 'Student profile not found'}, status=status.HTTP_404_NOT_FOUND)

        return Response({
            'data': {
                'name': user.name,
                'program': student.program,
                'image': user.profile_image.url if user.profile_image else None,
            }
        })


class TeacherInfoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        try:
            teacher = Teacher.objects.get(user=user)
        except Teacher.DoesNotExist:
            return Response({'message': 'Teacher profile not found'}, status=status.HTTP_404_NOT_FOUND)

        return Response({
            'data': {
                'name': user.name,
                'department': teacher.department,
                # Cloudinary URL — no hardcoded ngrok prefix
                'image': user.profile_image.url if user.profile_image else None,
            }
        })


# ==============================
# Course Offerings
# ==============================
class CourseOfferingListView(ListAPIView):
    serializer_class = CourseOfferingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = CourseOffering.objects.select_related("course")
        level = self.request.query_params.get("level")
        if level:
            queryset = queryset.filter(course__level=level)
        return queryset


class CourseView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        courses = Course.objects.all()
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data)


class CourseFilterView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, level):
        courses = Course.objects.filter(level=level)
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data)


# ==============================
# Enrollment
# ==============================
class EnrollStudentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = EnrollmentCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Enrollment successful!"}, status=status.HTTP_201_CREATED)


class MyEnrollmentsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        active_semester = Semester.objects.filter(is_active=True).first()
        if not active_semester:
            return Response({"message": "No active semester found", "enrollments": []})

        enrollments = Enrollment.objects.filter(
            student__user=request.user,
            course_offering__semester=active_semester
        ).select_related('course_offering__course', 'course_offering__semester')

        serializer = EnrollmentViewSerializer(enrollments, many=True)
        return Response(serializer.data)


# ==============================
# Attendance — Student
# ==============================
class VerifyAttendanceView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AttendanceCheckInSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        session = serializer.context['session']

        try:
            student = Student.objects.get(user=request.user)
        except Student.DoesNotExist:
            return Response({"detail": "Student profile not found"}, status=status.HTTP_404_NOT_FOUND)

        if Attendance.objects.filter(session=session, student=student).exists():
            return Response({"detail": "Attendance already marked."}, status=status.HTTP_400_BAD_REQUEST)

        Attendance.objects.create(session=session, student=student)

        added_students = serializer.validated_data.get('added_students', [])
        for matricule in added_students:
            try:
                added_student = Student.objects.get(matricule=matricule)
                if not Attendance.objects.filter(session=session, student=added_student).exists():
                    PendingAttendance.objects.get_or_create(
                        session=session,
                        added_student=added_student,
                        defaults={"adder": student, "approved": False, "rejected": False}
                    )
            except Student.DoesNotExist:
                continue

        return Response({"detail": "Attendance marked successfully."}, status=status.HTTP_200_OK)


class StudentCourseAttendanceDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, course_id):
        try:
            student = Student.objects.get(user=request.user)
        except Student.DoesNotExist:
            return Response({"detail": "Student not found"}, status=status.HTTP_404_NOT_FOUND)

        active_semester = Semester.objects.filter(is_active=True).first()
        if not active_semester:
            return Response({"detail": "No active semester"}, status=status.HTTP_404_NOT_FOUND)

        course_offering = CourseOffering.objects.filter(
            course__course_id=course_id,
            semester=active_semester
        ).first()
        if not course_offering:
            return Response({"detail": "Course not found"}, status=status.HTTP_404_NOT_FOUND)

        sessions = Session.objects.filter(course_offering=course_offering).order_by("start_time")

        attended_ids = set(
            Attendance.objects.filter(
                student=student, session__in=sessions
            ).values_list("session_id", flat=True)
        )

        result = [
            {
                "day": i,
                "session_id": s.session_id,
                "date": s.start_time,
                "status": "attended" if s.session_id in attended_ids else "missed",
            }
            for i, s in enumerate(sessions, start=1)
        ]

        serializer = StudentSessionAttendanceSerializer(result, many=True)
        return Response(serializer.data)


class StudentAttendanceSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, course_id):
        try:
            student = Student.objects.get(user=request.user)
        except Student.DoesNotExist:
            return Response({"detail": "Student not found"}, status=status.HTTP_404_NOT_FOUND)

        active_semester = Semester.objects.filter(is_active=True).first()
        if not active_semester:
            return Response({"detail": "No active semester"}, status=status.HTTP_404_NOT_FOUND)

        course_offering = CourseOffering.objects.filter(
            course__course_id=course_id, semester=active_semester
        ).first()
        if not course_offering:
            return Response({"detail": "Course not found"}, status=status.HTTP_404_NOT_FOUND)

        sessions = Session.objects.filter(course_offering=course_offering)
        total_sessions = sessions.count()
        attended = Attendance.objects.filter(student=student, session__in=sessions).count()

        data = {
            "total_sessions": total_sessions,
            "attended": attended,
            "missed": total_sessions - attended,
        }
        return Response(StudentAttendanceSummarySerializer(data).data)


# ==============================
# Sessions — Teacher
# ==============================
class LecturerAssignedCoursesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            teacher = Teacher.objects.get(user=request.user)
        except Teacher.DoesNotExist:
            return Response({"error": "Teacher profile not found"}, status=status.HTTP_404_NOT_FOUND)

        assignments = CourseAssignment.objects.select_related(
            "course_offering__course",
            "course_offering__semester"
        ).filter(lecturer=teacher, course_offering__semester__is_active=True)

        serializer = LecturerCourseAssignmentSerializer(assignments, many=True)
        return Response(serializer.data)


class StartSessionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        course_offering_id = request.data.get("course_offering")

        try:
            teacher = Teacher.objects.get(user=request.user)
        except Teacher.DoesNotExist:
            return Response({"error": "Teacher profile not found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            course_offering = CourseOffering.objects.select_related("semester").get(
                course_offering_id=course_offering_id
            )
        except CourseOffering.DoesNotExist:
            return Response({"error": "Course offering not found"}, status=status.HTTP_404_NOT_FOUND)

        if not course_offering.semester.is_active:
            return Response({"error": "Cannot start session for inactive semester"}, status=status.HTTP_400_BAD_REQUEST)

        if not CourseAssignment.objects.filter(lecturer=teacher, course_offering=course_offering).exists():
            return Response({"error": "You are not assigned to this course"}, status=status.HTTP_403_FORBIDDEN)

        if Session.objects.filter(course_offering=course_offering, active=True).exists():
            return Response({"error": "A session is already active for this course"}, status=status.HTTP_400_BAD_REQUEST)

        session = Session.objects.create(course_offering=course_offering)
        return Response(SessionSerializer(session).data, status=status.HTTP_201_CREATED)


class StopSessionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, session_id):
        try:
            teacher = Teacher.objects.get(user=request.user)
        except Teacher.DoesNotExist:
            return Response({"error": "Teacher profile not found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            session = Session.objects.select_related("course_offering").get(session_id=session_id)
        except Session.DoesNotExist:
            return Response({"error": "Session not found"}, status=status.HTTP_404_NOT_FOUND)

        if not CourseAssignment.objects.filter(lecturer=teacher, course_offering=session.course_offering).exists():
            return Response({"error": "Not authorized to stop this session"}, status=status.HTTP_403_FORBIDDEN)

        if not session.active:
            return Response({"error": "Session already closed"}, status=status.HTTP_400_BAD_REQUEST)

        session.active = False
        session.end_time = timezone.now()
        session.save()

        return Response({"message": "Session stopped successfully."})


# ==============================
# Attendance — Teacher views
# ==============================
class CourseSessionAttendanceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, session_id):
        try:
            teacher = Teacher.objects.get(user=request.user)
        except Teacher.DoesNotExist:
            return Response({"error": "Teacher profile not found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            session = Session.objects.select_related(
                "course_offering__course", "course_offering__semester"
            ).get(session_id=session_id)
        except Session.DoesNotExist:
            return Response({"error": "Session not found"}, status=status.HTTP_404_NOT_FOUND)

        if not session.course_offering.semester.is_active:
            return Response({"error": "Semester is not active"}, status=status.HTTP_400_BAD_REQUEST)

        if not CourseAssignment.objects.filter(
            lecturer=teacher, course_offering=session.course_offering
        ).exists():
            return Response({"error": "Not authorized to view this attendance"}, status=status.HTTP_403_FORBIDDEN)

        course_offering = session.course_offering

        total_sessions = Session.objects.filter(
            course_offering=course_offering,
            course_offering__semester__is_active=True
        ).count()

        attendance_stats = Attendance.objects.filter(
            session__course_offering=course_offering,
            session__course_offering__semester__is_active=True
        ).select_related("student__user").values(
            "student__matricule",
            "student__user__name",
            "student__user__profile_image",
        ).annotate(
            attended=Count("id"),
            last_attended=Max("created_at")
        )

        students_data = []
        for stat in attendance_stats:
            attended = stat["attended"]
            missed = total_sessions - attended

            session_attendance = Attendance.objects.filter(
                session=session,
                student__matricule=stat["student__matricule"]
            ).first()
            time = session_attendance.created_at.time() if session_attendance else None

            raw_image = stat['student__user__profile_image']
            image_url = None
            if raw_image:
                # raw_image is a Cloudinary public_id string when fetched via .values()
                from cloudinary.utils import cloudinary_url
                image_url, _ = cloudinary_url(str(raw_image))

            students_data.append({
                "matricule": stat["student__matricule"],
                "name": stat["student__user__name"],
                "image": image_url,
                "time": time,
                "attended": attended,
                "missed": missed,
                "last_attended": stat["last_attended"].date() if stat["last_attended"] else None,
            })

        serializer = CourseAttendanceStatsSerializer(students_data, many=True)
        return Response({
            "session_id": session.session_id,
            "course": course_offering.course.course_name,
            "total_sessions": total_sessions,
            "students": serializer.data,
        })


# ==============================
# Pending Attendance — Teacher
# ==============================
class PendingAttendanceListView(APIView):
    """
    GET /sessions/<session_id>/pending/
    Returns all unresolved pending students for a session.
    Used to hydrate the teacher's screen on load (WebSocket handles new arrivals).
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, session_id):
        try:
            teacher = Teacher.objects.get(user=request.user)
        except Teacher.DoesNotExist:
            return Response({"error": "Teacher profile not found"}, status=status.HTTP_404_NOT_FOUND)

        session = get_object_or_404(Session, session_id=session_id)

        if not CourseAssignment.objects.filter(
            lecturer=teacher, course_offering=session.course_offering
        ).exists():
            return Response({"error": "Not authorized"}, status=status.HTTP_403_FORBIDDEN)

        pending = PendingAttendance.objects.filter(
            session=session, approved=False, rejected=False
        ).select_related("adder__user", "added_student__user")

        serializer = PendingAttendanceSerializer(pending, many=True)
        return Response(serializer.data)


class ApprovePendingAttendanceView(APIView):
    """
    POST /approve-pending/
    Body: { "pending_ids": [1, 2, 3] }
    Approves the listed pending records and marks those students as attended.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        pending_ids = request.data.get("pending_ids", [])
        if not pending_ids:
            return Response({"error": "No pending_ids provided"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            teacher = Teacher.objects.get(user=request.user)
        except Teacher.DoesNotExist:
            return Response({"error": "Teacher profile not found"}, status=status.HTTP_404_NOT_FOUND)

        approved = []
        for pending_id in pending_ids:
            try:
                pending = PendingAttendance.objects.select_related(
                    "session__course_offering"
                ).get(id=pending_id, approved=False, rejected=False)
            except PendingAttendance.DoesNotExist:
                continue

            # Use the correct related_name defined on CourseAssignment
            if not CourseAssignment.objects.filter(
                lecturer=teacher,
                course_offering=pending.session.course_offering
            ).exists():
                continue

            pending.approved = True
            pending.save()

            Attendance.objects.get_or_create(
                session=pending.session,
                student=pending.added_student
            )
            approved.append(pending_id)

        return Response({
            "message": f"Approved {len(approved)} student(s).",
            "approved_ids": approved,
        })


class RejectPendingAttendanceView(APIView):
    """
    POST /reject-pending/
    Body: { "pending_ids": [1, 2, 3] }
    Rejects the listed pending records — student stays absent.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        pending_ids = request.data.get("pending_ids", [])
        if not pending_ids:
            return Response({"error": "No pending_ids provided"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            teacher = Teacher.objects.get(user=request.user)
        except Teacher.DoesNotExist:
            return Response({"error": "Teacher profile not found"}, status=status.HTTP_404_NOT_FOUND)

        rejected = []
        for pending_id in pending_ids:
            try:
                pending = PendingAttendance.objects.select_related(
                    "session__course_offering"
                ).get(id=pending_id, approved=False, rejected=False)
            except PendingAttendance.DoesNotExist:
                continue

            if not CourseAssignment.objects.filter(
                lecturer=teacher,
                course_offering=pending.session.course_offering
            ).exists():
                continue

            pending.rejected = True
            pending.save()
            rejected.append(pending_id)

        return Response({
            "message": f"Rejected {len(rejected)} student(s).",
            "rejected_ids": rejected,
        })