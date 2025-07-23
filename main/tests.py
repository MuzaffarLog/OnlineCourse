# tests.py
from django.test import TestCase
from rest_framework.test import APIClient
from users.models import User
from main.models import Course, Payment

class EnrollCourseTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.student = User.objects.create_user(
            username='student1',
            password='pass1234',
            role='STUDENT'
        )
        self.course = Course.objects.create(title="Python")
        Payment.objects.create(user=self.student, course=self.course, status='completed')

    def test_enroll_course_success(self):
        self.client.login(username='student1', password='pass1234')
        response = self.client.post(f'/api/courses/{self.course.id}/enroll/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['detail'], "Muvaffaqiyatli yozildingiz!")

