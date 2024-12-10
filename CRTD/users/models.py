from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.utils.timezone import now, timedelta


class User(models.Model):
    id = models.BigAutoField(primary_key=True)
    full_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    contact_number = models.CharField(max_length=15)
    password = models.CharField(max_length=255)  # Hashed password
    is_email_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        self.save()

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)


class Passkey(models.Model):
    key = models.CharField(max_length=255, default="CRTD@2025")  # Company passkey
    is_active = models.BooleanField(default=True)


class OTP(models.Model):
    email = models.EmailField()  # Store email associated with the OTP
    otp_code = models.CharField(max_length=6)  # Store the OTP code
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp for when OTP was created

    def is_expired(self):
        """
        Check if the OTP has expired.
        You can adjust the expiration time by modifying `valid_duration`.
        """
        valid_duration = timedelta(minutes=10)  # OTP valid for 10 minutes
        return now() > self.created_at + valid_duration

    def __str__(self):
        return f"OTP for {self.email} - {self.otp_code}"


class Section(models.Model):
    name = models.CharField(max_length=100)
    order = models.PositiveIntegerField(unique=True)  # To define section sequence


class Question(models.Model):
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField()
    options = models.JSONField()  # Store options as a list of JSON objects
    correct_option = models.CharField(max_length=50)


class UserExamProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="exam_progress")
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name="user_progress")
    is_attempted = models.BooleanField(default=False)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)


class UserResponse(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="responses")
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_option = models.CharField(max_length=50)
    is_correct = models.BooleanField(default=False)


