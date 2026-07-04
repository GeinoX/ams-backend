from django.shortcuts import render
from .serializers import CreateSessionSerializer
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from core.permissions import IsLecturer
from .models import Session
from courses.models import CourseAssignment
from django.utils import timezone
from rest_framework.response import Response
from rest_framework import status
from auth_app.models import Lecturer
from .services import mark_remaining_students_absent
from django.db import transaction



# Create your views here.

class SessionCreateView(CreateAPIView):
    permission_classes = [IsAuthenticated ,IsLecturer]
    
    serializer_class = CreateSessionSerializer


"""
  1. Check authentication and the lecturer permissions.
  2. Get the session.
  3. Verifu the lecturer is assigned to the course.
  4. Verify the sessuib is still active.
  5. End the session adn mark the remaining students absent inside the transaction.
"""
class SessionEndView(APIView):
    permission_classes = [IsAuthenticated ,IsLecturer]

    def patch(self, request, session_id):
        teacher = Lecturer.objects.get(user=request.user) 
        try:
            session = Session.objects.select_related("course_offering").get(session_id=session_id)
        except Session.DoesNotExist:
            return Response({"error": "Session not found"}, status=status.HTTP_404_NOT_FOUND)

        if not CourseAssignment.objects.filter(lecturer=teacher, course_offering=session.course_offering).exists():
            return Response({"error": "Not authorized to stop this session"}, status=status.HTTP_403_FORBIDDEN)
        
        if not session.active:
            return Response({"error": "Not authorized to stop the session"}, status=status.HTTP_400_BAD_REQUEST)
        
        with transaction.atomic():
            session.active = False
            session.end_time = timezone.now()
        
            session.save()
            mark_remaining_students_absent(session=session)
        

        return Response({"message": "Session ended successfully"}, status=status.HTTP_200_OK)


