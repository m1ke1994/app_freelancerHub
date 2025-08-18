from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


phone_validator = RegexValidator(
    regex=r'^\+7\d{10}$',
    message='Телефон должен быть в формате +7XXXXXXXXXX (10 цифр после +7).'
)


class User(AbstractUser):
    # Делаем email уникальным
    email = models.EmailField(unique=True)

    # Телефон (временно опционален, чтобы пройти миграции; позже можно убрать null/blank)
    phone = models.CharField(
        max_length=16,
        unique=True,
        null=True,
        blank=True,
        validators=[phone_validator],
        help_text='Формат: +79991234567'
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
        default=ROLE_EXECUTOR
    )

    def __str__(self):
        return self.username or self.email
