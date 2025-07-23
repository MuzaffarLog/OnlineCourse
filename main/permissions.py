from rest_framework import permissions

class IsTeacher(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated and request.user.role == "TEACHER":
            return True
        return False

class IsStudent(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated and request.user.role == "STUDENT":
            return True
        return False

# Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzYwOTc4MDAxLCJpYXQiOjE3NTMyMDIwMDEsImp0aSI6IjY4OTcxM2QwNjhlNTRmNmE4NTczNGJlZWE1YWQwZDdjIiwidXNlcl9pZCI6IjIifQ.4zfxeomtQCSRxzs1L75WFlj-mv0PL3PGphpxQQj2EdU
# Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzYwOTc2NDA4LCJpYXQiOjE3NTMyMDA0MDgsImp0aSI6ImVmYjcxNTIxNDFkYjRmNTliZGY4NDdmNzMwNTkzNWM1IiwidXNlcl9pZCI6IjEifQ.tvCScVVivqHmp7VgOF0b5wC1TgmM9Z0DEvkz8zfzBPQ