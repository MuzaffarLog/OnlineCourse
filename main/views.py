from django.db.models import Q
from rest_framework import status
from rest_framework.generics import *
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .serializers import *
from .permissions import *
from users.serializers import *
from main.throttling import ReviewRateThrottle

class CourseCreateView(CreateAPIView):
    queryset = Course.objects.all()
    permission_classes = [IsTeacher]
    serializer_class = CoursesSerializer


    def perform_create(self, serializer):
        course = serializer.save()
        self.request.user.course.add(course)


class CourseRetrieveView(APIView):
    permission_classes = [IsTeacher]

    @swagger_auto_schema(
        operation_description="Teacher can view all courses with filtering",
        manual_parameters=[
            openapi.Parameter('search', openapi.IN_QUERY, description='Search by course title', type=openapi.TYPE_STRING),
            openapi.Parameter('min_price', openapi.IN_QUERY, description='Filter by min price', type=openapi.TYPE_NUMBER),
            openapi.Parameter('max_price', openapi.IN_QUERY, description='Filter by max price', type=openapi.TYPE_NUMBER),
            openapi.Parameter(
                name='ordering',
                in_=openapi.IN_QUERY,
                description='Order by price or created_at',
                type=openapi.TYPE_STRING,
                enum=['price', '-price', 'created_at', '-created_at']
            ),
        ]
    )
    def get(self, request):
        courses = Course.objects.all()

        search = request.GET.get('search')
        if search:
            courses = courses.filter(title__icontains=search)

        min_price = request.GET.get('min_price')
        if min_price:
            try:
                courses = courses.filter(price__gte=float(min_price))
            except ValueError:
                pass

        max_price = request.GET.get('max_price')
        if max_price:
            try:
                courses = courses.filter(price__lte=float(max_price))
            except ValueError:
                pass

        ordering = request.GET.get('ordering')
        if ordering in ['price', '-price', 'created_at', '-created_at']:
            courses = courses.order_by(ordering)

        serializer = CoursesSerializer(courses, many=True)
        return Response(serializer.data)


class CourseRetrieveUpdateDestroyView(APIView):
    permission_classes = [IsTeacher]

    def get_object(self, pk, user):
        # Teacherga tegishli kursni topish, aks holda 404
        return get_object_or_404(user.course.all(), pk=pk)

    def get(self, request, pk):
        course = self.get_object(pk, request.user)
        serializer = CoursesSerializer(course)
        return Response(serializer.data)

    def put(self, request, pk):
        course = self.get_object(pk, request.user)
        serializer = CoursesSerializer(course, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def patch(self, request, pk):
        course = self.get_object(pk, request.user)
        serializer = CoursesSerializer(course, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        course = self.get_object(pk, request.user)
        course.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



class LessonCourseRetrieveView(APIView):
    permission_classes = [IsTeacher]

    def get(self, request, pk):
        course = get_object_or_404(Course, id=pk)
        lessons = Lesson.objects.filter(course=course)
        serializer = LessonSerializer(lessons, many=True)
        return Response(serializer.data)


class LessonRetrieveCreateUpdateDeleteView(APIView):
    permission_classes = [IsTeacher]

    def post(self, request, pk):
        course = get_object_or_404(request.user.course.all(), id=pk)
        serializer = LessonSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(course=course)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request, pk):
        lesson = get_object_or_404(Lesson, id=pk)
        serializer = LessonSerializer(lesson)
        return Response(serializer.data)

    def put(self, request, pk):
        lesson = get_object_or_404(Lesson, id=pk, course__in=request.user.course.all())
        serializer = LessonSerializer(lesson, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def patch(self, request, pk):
        lesson = get_object_or_404(Lesson, id=pk, course__in=request.user.course.all())
        serializer = LessonSerializer(lesson, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        lesson = get_object_or_404(Lesson, id=pk, course__in=request.user.course.all())
        lesson.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MakePaymentView(APIView):
    permission_classes = [IsStudent]  # Faqat student to‘lov qilishi mumkin

    def post(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)
        amount = request.data.get('amount')

        if not amount:
            return Response({'detail': 'Amount is required.'}, status=status.HTTP_400_BAD_REQUEST)

        payment = Payment.objects.create(
            user=request.user,
            course=course,
            amount=amount,
            status='completed'  # Fake gateway; haqiqiy gateway bo‘lsa: pending
        )
        serializer = PaymentSerializer(payment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UserPaymentsListView(APIView):
    permission_classes = [IsTeacher]

    def get(self, request):
        payments = Payment.objects.all()
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data)

class EnrollCourseView(APIView):
    permission_classes = [IsStudent]

    def post(self, request, course_id):
        user = request.user
        if user.role != 'STUDENT':
            return Response({"detail": "Faqat o‘quvchilar kursga yozilishi mumkin."}, status=403)

        course = get_object_or_404(Course, id=course_id)

        # To‘lov tekshiruvi
        if not Payment.objects.filter(user=user, course=course, status='completed').exists():
            return Response({"detail": "To‘lov mavjud emas."}, status=403)

        user.course.add(course)
        return Response({"detail": "Muvaffaqiyatli yozildingiz!"}, status=200)


class CourseStudentsListAPIView(APIView):
    permission_classes = [IsTeacher]

    def get(self, request, course_id):
        user = request.user
        if user.role != 'TEACHER':
            return Response({"detail": "Faqat ustozlar ko‘rishi mumkin."}, status=403)

        course = get_object_or_404(Course, id=course_id)


        students = User.objects.filter(course=course, role='STUDENT')
        serializer = UserSerializer(students, many=True)
        return Response(serializer.data)


class ReviewCreateView(APIView):
    permission_classes = [IsStudent]
    throttle_classes = [ReviewRateThrottle]

    def post(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)

        # Student o‘sha kursga yozilganmi tekshiramiz
        if course not in request.user.course.all():
            return Response({"detail": "Siz bu kursga yozilmagansiz."}, status=status.HTTP_403_FORBIDDEN)

        # Avval sharh qoldirgan bo‘lsa, qayta ruxsat bermaymiz
        if Review.objects.filter(student=request.user, course=course).exists():
            return Response({"detail": "Siz bu kursga allaqachon sharh qoldirgansiz."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(student=request.user, course=course)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CourseReviewListForTeacher(APIView):
    permission_classes = [IsTeacher]

    def get(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)

        # Kurs sizga tegishliligini tekshiramiz
        if course not in request.user.course.all():
            return Response({"detail": "Bu kurs sizga tegishli emas."}, status=status.HTTP_403_FORBIDDEN)

        reviews = Review.objects.filter(course=course)
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
