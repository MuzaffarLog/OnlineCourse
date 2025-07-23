from rest_framework import generics
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import get_object_or_404

from main.permissions import *

from .serializers import *


class RegisterView(generics.CreateAPIView):
    permission_classes = (permissions.AllowAny,)
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

class UsersRetrieveAPIView(generics.RetrieveAPIView):
    permission_classes = [IsTeacher]
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user



class StudentInformationRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsStudent]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user



class TeacherInformationRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsTeacher]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class StudentManageByTeacherAPIView(generics.RetrieveUpdateDestroyAPIView):

    serializer_class = UserSerializer
    permission_classes = [IsTeacher]
    queryset = User.objects.filter(role=User.Role.student)

    lookup_field = 'pk'

    def get_object(self):
        # Faqat teacher foydalanuvchi amal bajara oladi
        user = self.request.user
        if user.role != User.Role.teacher:
            raise PermissionDenied("Faqat teacher foydalanuvchilar bu amalni bajara oladi.")

    def get_object(self):
        pk = self.kwargs.get("pk")
        if not pk:
            raise PermissionDenied("Studentning ID (pk) kerak.")

        student = get_object_or_404(User, pk=pk, role=User.Role.student)
        return student
