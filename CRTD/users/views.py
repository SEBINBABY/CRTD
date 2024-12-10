from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Passkey
from .models import User, UserResponse, UserExamProgress, OTP
import random
from django.core.mail import send_mail
from django.conf import settings
from django.utils.timezone import now
from .models import Section, UserExamProgress, Question
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
import re

# Password validation function
def is_valid_password(password):
    if len(password) < 8:
        return "Password must be at least 8 characters long."
    if not re.search(r"[A-Z]", password):
        return "Password must contain at least one uppercase letter."
    if not re.search(r"[a-z]", password):
        return "Password must contain at least one lowercase letter."
    if not re.search(r"[0-9]", password):
        return "Password must contain at least one digit."
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return "Password must contain at least one special character."
    return None  # No issues

def verify_passkey(request):
    if request.method == "POST":
        passkey = request.POST.get("passkey")
        if Passkey.objects.filter(key=passkey, is_active=True).exists():
            return redirect("login")
        else:
            messages.error(request, "Invalid Passkey!")
    return render(request, "verify_passkey.html")

# Registration View
def register(request):
    if request.method == "POST":
        full_name = request.POST.get("full_name")
        email = request.POST.get("email")
        contact_number = request.POST.get("contact_number")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect("register")
        # Validate password strength
        password_error = is_valid_password(password)
        if password_error:
            messages.error(request, password_error)
            return redirect("register")
        # Ensure the email has been verified before creating the user
        try:
            otp_instance = OTP.objects.get(email=email)
            if not otp_instance.is_expired():
                # Email verified, proceed with registration
                user = User.objects.create(
                    full_name=full_name,
                    email=email,
                    contact_number=contact_number,
                )
                user.set_password(password)
                user.is_email_verified = True
                user.save()
                return render(request, "created_account_success.html")
            else:
                messages.error(request, "OTP has expired! Please verify email again.")
                return redirect("register")
        except OTP.DoesNotExist:
            messages.error(request, "Email verification is required!")
            return redirect("register")
    return render(request, "register.html")

def login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                request.session["user_id"] = user.id
                return render("instructions_page.html")
            else:
                messages.error(request, "Invalid email or password!")
        except User.DoesNotExist:
            messages.error(request, "Invalid email or password!")
    return render(request, "login.html")

# View to send OTP
@csrf_exempt
def send_email_verification_otp(request):
    if request.method == "POST":
        email = request.POST.get("email")
        if not email:
            messages.error(request, "Email is required!")
        if User.objects.filter(email=email).exists():
            messages.success(request, "Email is already registered!")
        request.session["email_for_otp"] = email  # Save email to session
        otp_code = random.randint(1000, 9999)
        # Save or update the OTP
        OTP.objects.update_or_create(email=email, defaults={"otp_code": str(otp_code)})
        # Send OTP email
        context = {"otp_code": otp_code}
        email_subject = "Email Verification Code"
        email_body = render_to_string("email_message.txt", context)
        send_mail(
            email_subject,
            email_body,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )
        messages.success(request, "OTP sent successfully! Please check your registered mail.")
        return render(request,"otp.html")
    messages.error(request, "Invalid request method!")
  
# View to verify OTP
@csrf_exempt
def verify_email_otp(request):
    if request.method == "POST":
        email = request.POST.get("email")
        otp_code = (
            request.POST.get("otp1", "") +
            request.POST.get("otp2", "") +
            request.POST.get("otp3", "") +
            request.POST.get("otp4", "")
        )
        if not email or not otp_code:
            messages.error(request, "Email and OTP are required!")
        try:
            otp_instance = OTP.objects.get(email=email)
            if otp_instance.otp_code == otp_code and not otp_instance.is_expired():
                messages.success(request, "Email verified successfully! Continue with the registration")
                return redirect("register")
            elif otp_instance.is_expired():
                messages.error(request, "OTP has expired! Verify your email again")
                return redirect("register")
            else:
                messages.error(request, "Invalid OTP!")
                return redirect("register")          
        except OTP.DoesNotExist:
            messages.error(request, "No OTP found for this email!")
            return redirect("register") 
    messages.error(request, "Invalid request method!")
    return redirect("register") 

"""
def start_exam(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login")

    sections = Section.objects.all().order_by("order")
    user_progress, created = UserExamProgress.objects.get_or_create(
        user_id=user_id,
        section=sections.first(),
        defaults={"start_time": now()},
    )
    return redirect("exam_section", section_id=user_progress.section.id)


def exam_section(request, section_id):
    section = Section.objects.get(id=section_id)
    questions = section.questions.all()

    if request.method == "POST":
        for question in questions:
            selected_option = request.POST.get(f"question_{question.id}")
            UserResponse.objects.create(
                user_id=request.session.get("user_id"),
                question=question,
                selected_option=selected_option,
                is_correct=(selected_option == question.correct_option),
            )
        user_progress = UserExamProgress.objects.get(
            user_id=request.session.get("user_id"), section=section
        )
        user_progress.is_attempted = True
        user_progress.end_time = now()
        user_progress.save()

        next_section = Section.objects.filter(order__gt=section.order).first()
        if next_section:
            return redirect("exam_section", section_id=next_section.id)
        return redirect("exam_complete")
    return render(request, "exam_section.html", {"section": section, "questions": questions})


def exam_complete(request):
    return render(request, "exam_complete.html")
from django.shortcuts import render

"""

def response(request):
    return render(request, "otp.html")