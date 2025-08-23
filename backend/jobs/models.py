from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

User = settings.AUTH_USER_MODEL


class Job(models.Model):
    class BudgetType(models.TextChoices):
        FIXED = 'fixed', _('Фиксированный')
        RANGE = 'range', _('Диапазон')

    class DeadlineType(models.TextChoices):
        FLEXIBLE = 'flexible', _('Гибкий')
        STRICT = 'strict', _('Строгий')

    CATEGORIES = [
        ("Веб-разработка", "Веб-разработка"),
        ("Мобильные приложения", "Мобильные приложения"),
        ("Дизайн", "Дизайн"),
        ("Копирайтинг", "Копирайтинг"),
        ("SEO и маркетинг", "SEO и маркетинг"),
        ("Переводы", "Переводы"),
    ]

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='jobs',
        verbose_name=_('Владелец'),
        db_index=True,
    )

    title = models.CharField(_('Название'), max_length=200)
    category = models.CharField(_('Категория'), max_length=64, choices=CATEGORIES)
    description = models.TextField(_('Описание'))

    # JSON-массив строк
    skills = models.JSONField(_('Навыки'), default=list, blank=True)

    budget_type = models.CharField(
        _('Тип бюджета'),
        max_length=16,
        choices=BudgetType.choices,
        default=BudgetType.FIXED
    )
    budget_fixed = models.PositiveIntegerField(_('Фиксированный бюджет (₽)'), null=True, blank=True)
    budget_min = models.PositiveIntegerField(_('Бюджет от (₽)'), null=True, blank=True)
    budget_max = models.PositiveIntegerField(_('Бюджет до (₽)'), null=True, blank=True)

    deadline = models.CharField(_('Срок выполнения (текст)'), max_length=120, blank=True)
    deadline_type = models.CharField(
        _('Тип дедлайна'),
        max_length=16,
        choices=DeadlineType.choices,
        default=DeadlineType.FLEXIBLE
    )

    location = models.CharField(_('Местоположение'), max_length=120, blank=True)
    remote = models.BooleanField(_('Удалённо'), default=True)
    urgent = models.BooleanField(_('Срочное'), default=False)

    # Статусы
    is_active = models.BooleanField(_('Активно'), default=True)
    canceled_at = models.DateTimeField(_('Отменено в'), null=True, blank=True)
    canceled_reason = models.CharField(_('Причина отмены'), max_length=255, blank=True)

    # Служебные
    created_at = models.DateTimeField(_('Создано'), auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(_('Обновлено'), auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Задание')
        verbose_name_plural = _('Задания')

    def __str__(self):
        return f'#{self.pk} {self.title[:50]}'

    @property
    def status(self) -> str:
        """
        Для фронта: 'pending' | 'canceled_by_customer'
        (при необходимости можно расширить до in_progress/completed и т.п.)
        """
        return 'pending' if self.is_active else 'canceled_by_customer'

    def cancel(self, reason: str = ""):
        """Отменить задание владельцем."""
        self.is_active = False
        self.canceled_at = timezone.now()
        self.canceled_reason = (reason or "")[:255]
        self.save(update_fields=['is_active', 'canceled_at', 'canceled_reason', 'updated_at'])

    def clean(self):
        """
        Бизнес-валидация:
        - FIXED → требуется budget_fixed
        - RANGE → требуются budget_min/budget_max и min<=max
        """
        from django.core.exceptions import ValidationError

        if self.budget_type == self.BudgetType.FIXED:
            if not self.budget_fixed:
                raise ValidationError(_('Для фиксированного бюджета необходимо указать "budget_fixed".'))
            self.budget_min = None
            self.budget_max = None

        elif self.budget_type == self.BudgetType.RANGE:
            if self.budget_min is None or self.budget_max is None:
                raise ValidationError(_('Для диапазона необходимо указать "budget_min" и "budget_max".'))
            if self.budget_min > self.budget_max:
                raise ValidationError(_('Значение "budget_min" не может быть больше "budget_max".'))
            self.budget_fixed = None


def job_attachment_path(instance: 'JobAttachment', filename: str) -> str:
    # media/job_attachments/<job_id>/<filename>
    return f'job_attachments/{instance.job_id}/{filename}'


class JobAttachment(models.Model):
    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name='attachments',
        verbose_name=_('Задание')
    )
    file = models.FileField(_('Файл'), upload_to=job_attachment_path)
    uploaded_at = models.DateTimeField(_('Загружено'), auto_now_add=True)
    original_name = models.CharField(_('Оригинальное имя файла'), max_length=255, blank=True)

    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = _('Файл задания')
        verbose_name_plural = _('Файлы задания')

    def __str__(self):
        return f'Attachment #{self.pk} for Job #{self.job_id}'
