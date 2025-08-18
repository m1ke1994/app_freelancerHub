# users/models.py
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

phone_validator = RegexValidator(
    regex=r'^\+7\d{10}$',
    message='Телефон должен быть в формате +7XXXXXXXXXX (10 цифр после +7).'
)

def avatar_upload_to(instance, filename):
    return f"avatars/{instance.id or 'tmp'}/{filename}"

class User(AbstractUser):
    email = models.EmailField(unique=True)

    phone = models.CharField(
        max_length=16,
        unique=True,
        null=True,
        blank=True,
        validators=[phone_validator],
        help_text='Формат: +79991234567',
    )

    ROLE_EXECUTOR = 'executor'
    ROLE_CUSTOMER = 'customer'
    ROLE_CHOICES = [
        (ROLE_EXECUTOR, 'Исполнитель'),
        (ROLE_CUSTOMER, 'Заказчик'),
    ]
    role = models.CharField(max_length=16, choices=ROLE_CHOICES, default=ROLE_EXECUTOR)

    avatar = models.ImageField(upload_to=avatar_upload_to, blank=True, null=True)

    # ====== ПОЛЯ АНКЕТЫ ======
    title = models.CharField(max_length=255, blank=True, default="")
    bio = models.TextField(blank=True, default="")
    location = models.CharField(max_length=255, blank=True, default="")
    gender = models.CharField(max_length=32, blank=True, default="")         # "Мужской" | "Женский" | "" (Не указывать)
    education = models.CharField(max_length=64, blank=True, default="")      # из вашего справочника
    status = models.CharField(max_length=16, blank=True, default="open")     # "open" | "partial" | "busy"

    categories = models.JSONField(default=list, blank=True)  # [string]
    skills = models.JSONField(default=list, blank=True)      # [string]

    RATE_HOUR = 'hour'
    RATE_PROJECT = 'project'
    RATE_CHOICES = [(RATE_HOUR, 'Час'), (RATE_PROJECT, 'Проект')]
    rate_type = models.CharField(max_length=16, choices=RATE_CHOICES, default=RATE_HOUR)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    project_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    availability = models.BooleanField(default=True)

    links = models.JSONField(default=list, blank=True)       # [{label,url}]
    socials = models.JSONField(default=dict, blank=True)     # {telegram, linkedin}
    portfolio = models.JSONField(default=list, blank=True)   # [{title,url}]
    busy_dates = models.JSONField(default=list, blank=True)  # ["YYYY-MM-DD"]

    def save(self, *args, **kwargs):
        if self.email:
            self.email = self.email.strip().lower()
        if not self.username and self.email:
            self.username = self.email
        super().save(*args, **kwargs)

    @property
    def avatar_url(self) -> str | None:
        try:
            return self.avatar.url if self.avatar else None
        except Exception:
            return None

    def __str__(self):
        return self.username or self.email

    class Meta:
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['phone']),
        ]
