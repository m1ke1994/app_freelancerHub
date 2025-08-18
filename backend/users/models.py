# users/models.py
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

phone_validator = RegexValidator(
    regex=r'^\+7\d{10}$',
    message='Телефон должен быть в формате +7XXXXXXXXXX (10 цифр после +7).'
)

def avatar_upload_to(instance, filename):
    # /avatars/<user_id или tmp>/<filename>
    return f"avatars/{instance.id or 'tmp'}/{filename}"

class User(AbstractUser):
    # Email — уникальный (мы приводим к lower() в save, так что отдельный ci-constraint не нужен)
    email = models.EmailField(unique=True)

    # Телефон (может быть пустым)
    phone = models.CharField(
        max_length=16,
        unique=True,
        null=True,
        blank=True,
        validators=[phone_validator],
        help_text='Формат: +79991234567',
    )

    # Роль
    ROLE_EXECUTOR = 'executor'
    ROLE_CUSTOMER = 'customer'
    ROLE_CHOICES = [
        (ROLE_EXECUTOR, 'Исполнитель'),
        (ROLE_CUSTOMER, 'Заказчик'),
    ]
    role = models.CharField(
        max_length=16,
        choices=ROLE_CHOICES,
        default=ROLE_EXECUTOR,
    )

    # Аватар
    avatar = models.ImageField(upload_to=avatar_upload_to, blank=True, null=True)

    def save(self, *args, **kwargs):
        # нормализуем email и username
        if self.email:
            self.email = self.email.strip().lower()
        if not self.username and self.email:
            self.username = self.email
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username or self.email

    @property
    def avatar_url(self) -> str | None:
        try:
            return self.avatar.url if self.avatar else None
        except Exception:
            return None

    class Meta:
        # БЕЗ UniqueConstraint(expressions=...), чтобы не падало на версии Django
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['phone']),
        ]
