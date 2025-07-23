from django.urls import path
from .views import *

urlpatterns = [
    path('course-create/', CourseCreateView.as_view(), name='course-create'),
    path('course-all-retrieve/', CourseRetrieveView.as_view(), name='course-all-retrieve'),
    path('course-retrieve-update-destroy/<int:pk>/', CourseRetrieveUpdateDestroyView.as_view(), name='course-retrieve-update-destroy'),
    path('lesson-course-retrieve/<int:pk>/', LessonCourseRetrieveView.as_view(), name='lesson-retrieve'),
    path('lesson-course-retrieve-update-delete/<int:pk>/',LessonRetrieveCreateUpdateDeleteView.as_view(), name='lesson-retrieve-update-delete' ),
    path('courses/<int:course_id>/pay/', MakePaymentView.as_view(), name='make-payment'),
    path('payments/', UserPaymentsListView.as_view(), name='user-payments'),
    path('api/courses/<int:course_id>/enroll/', EnrollCourseView.as_view(), name='course-enroll'),
    path('api/courses/<int:course_id>/students/', CourseStudentsListAPIView.as_view(), name='course-students'),
    path('api/courses/<int:course_id>/reviews/', ReviewCreateView.as_view(), name='student-review-create'),
    path('api/courses/<int:course_id>/reviews/teacher/', CourseReviewListForTeacher.as_view(), name='teacher-review-list'),

]
