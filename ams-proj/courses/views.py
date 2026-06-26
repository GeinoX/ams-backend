from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny


# Create your views here.

class CourseListView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self):