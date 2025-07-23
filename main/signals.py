from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.core.mail import send_mail
from users.models import User
from main.models import Course

@receiver(m2m_changed, sender=User.course.through)
def send_course_enroll_email(sender, instance, action, reverse, pk_set, **kwargs):
    if action == 'post_add' and instance.role == User.Role.student:
        for course_id in pk_set:
            course = Course.objects.filter(id=course_id).first()
            if not course:
                continue

            # Teacherga yuborish
            teachers = User.objects.filter(course=course, role=User.Role.teacher)
            for teacher in teachers:
                send_mail(
                    subject='Yangi o‘quvchi qo‘shildi',
                    message=f"{instance.username} {course.title} kursiga yozildi.",
                    from_email='noreply@example.com',
                    recipient_list=[teacher.email],
                    fail_silently=True
                )

            # Studentga yuborish
            send_mail(
                subject="Xush kelibsiz!",
                message=f"{course.title} kursiga yozildingiz. Omad!",
                from_email="noreply@example.com",
                recipient_list=[instance.email],
                fail_silently=True
            )
