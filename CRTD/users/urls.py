from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path("", views.verify_passkey, name="verify_passkey"),
    path("register/", views.register, name="register"),
    path("login/", views.login, name="login"),
    path("send_email_verification_otp/", views.send_email_verification_otp, name="send_email_verification_otp"),
    path("verify_email_otp/", views.verify_email_otp, name="verify_email_otp"),
    # path("exam-instructions/", views.exam_instructions, name="exam_instructions"),
    # path("start-exam/", views.start_exam, name="start_exam"),
    # path("exam-section/<int:section_id>/", views.exam_section, name="exam_section"),
    # path("exam-complete/", views.exam_complete, name="exam_complete"),

    path('response/', views.response, name='response')
]