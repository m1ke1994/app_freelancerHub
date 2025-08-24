from __future__ import annotations

import os
import re
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

User = settings.AUTH_USER_MODEL


def _sanitize_filename(name: str) -> str:
    """
    Приводим имя к безопасному виду:
    - убираем управляющие/опасные символы
    - не допускаем пустое имя
    """
    name = os.path.basename(name or "").strip()
    if not name:
        return "file"
    # оставляем буквы/цифры/.-_ и пробелы; остальное заменяем на '-'
    name = re.sub(r"[^A-Za-z0-9а-яА-ЯёЁ\.\-_ ]+", "-", name)
    # убираем повторяющиеся дефисы и пробелы по краям
    name = re.sub(r"-{2,}", "-", name).strip(" -")
    return name or "file"


def job_attachment_path(instance: "JobAttachment", filename: str) -> str:
    """
    Путь: media/job_attachments/<job_id>/<normalized-filename>
    """
    safe_name = _sanitize_filename(filename)
    return f"job_attachments/{instance.job_id}/{safe_name}"


class Job(models.Model):
    class BudgetType(models.TextChoices):
        FIXED = "fixed", _("Фиксированный")
        RANGE = "range", _("Диапазон")

    class DeadlineType(models.TextChoices):
        FLEXIBLE = "flexible", _("Гибкий")
        STRICT = "strict", _("Строгий")

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
        related_name="jobs",
        verbose_name=_("Владелец"),
        db_index=True,
    )

    title = models.CharField(_("Название"), max_length=200)
    category = models.CharField(_("Категория"), max_length=64, choices=CATEGORIES)
    description = models.TextField(_("Описание"))

    # JSON-массив строк
    skills = models.JSONField(_("Навыки"), default=list, blank=True)

    budget_type = models.CharField(
        _("Тип бюджета"),
        max_length=16,
        choices=BudgetType.choices,
        default=BudgetType.FIXED,
    )
    budget_fixed = models.PositiveIntegerField(_("Фиксированный бюджет (₽)"), null=True, blank=True)
    budget_min = models.PositiveIntegerField(_("Бюджет от (₽)"), null=True, blank=True)
    budget_max = models.PositiveIntegerField(_("Бюджет до (₽)"), null=True, blank=True)

    deadline = models.CharField(_("Срок выполнения (текст)"), max_length=120, blank=True)
    deadline_type = models.CharField(
        _("Тип дедлайна"),
        max_length=16,
        choices=DeadlineType.choices,
        default=DeadlineType.FLEXIBLE,
    )

    location = models.CharField(_("Местоположение"), max_length=120, blank=True)
    remote = models.BooleanField(_("Удалённо"), default=True)
    urgent = models.BooleanField(_("Срочное"), default=False)

    # Статусы
    is_active = models.BooleanField(_("Активно"), default=True)
    canceled_at = models.DateTimeField(_("Отменено в"), null=True, blank=True)
    canceled_reason = models.CharField(_("Причина отмены"), max_length=255, blank=True)

    # Служебные
    created_at = models.DateTimeField(_("Создано"), auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(_("Обновлено"), auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Задание")
        verbose_name_plural = _("Задания")

    def __str__(self) -> str:  # pragma: no cover
        return f"#{self.pk} {self.title[:50]}"

    @property
    def status(self) -> str:
        """
        Для фронта: 'pending' | 'canceled_by_customer'
        (при необходимости можно расширить до in_progress/completed и т.п.)
        """
        return "pending" if self.is_active else "canceled_by_customer"

    def cancel(self, reason: str = "") -> None:
        """Отменить задание владельцем."""
        self.is_active = False
        self.canceled_at = timezone.now()
        self.canceled_reason = (reason or "")[:255]
        self.save(update_fields=["is_active", "canceled_at", "canceled_reason", "updated_at"])

    def clean(self) -> None:
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


class JobAttachment(models.Model):
    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name="attachments",
        verbose_name=_("Задание"),
    )
    file = models.FileField(_("Файл"), upload_to=job_attachment_path)
    uploaded_at = models.DateTimeField(_("Загружено"), auto_now_add=True)
    original_name = models.CharField(_("Оригинальное имя файла"), max_length=255, blank=True)

    class Meta:
        ordering = ["-uploaded_at"]
        verbose_name = _("Файл задания")
        verbose_name_plural = _("Файлы задания")

    def __str__(self) -> str:  # pragma: no cover
        return f"Attachment #{self.pk} for Job #{self.job_id}"

    def save(self, *args, **kwargs) -> None:
        """
        Автозаполнение original_name, нормализация имени файла.
        """
        if self.file and not self.original_name:
            self.original_name = os.path.basename(getattr(self.file, "name", "") or "").strip()
        # Если storage ещё не определил имя, нормализуем руками для upload_to
        if self.file and getattr(self.file, "name", None):
            base = os.path.basename(self.file.name)
            safe = _sanitize_filename(base)
            # Обновляем имя только если оно изменилось после нормализации
            if safe and safe != base:
                # Важно: менять только отображаемое имя перед сохранением.
                self.file.name = safe
        super().save(*args, **kwargs)

    # Удобные свойства — их можно сериализовать как read-only
    @property
    def file_url(self) -> str:
        try:
            return self.file.url
        except Exception:
            return ""

    @property
    def filename(self) -> str:
        return self.original_name or os.path.basename(self.file.name or "") or "file"
