from __future__ import annotations

from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from .models import Job, JobAttachment

# Подтягиваем публичный сериализатор владельца
from users.serializers import OwnerPublicSerializer


class JobSerializer(serializers.ModelSerializer):
    """
    Сериализатор задания под клиентский визард и каталог.
    Поддерживает оба типа бюджета и массив навыков.
    """
skills = serializers.ListField(
    child=serializers.CharField(max_length=64),
    required=False,
    allow_empty=True,
    allow_null=True,   # <—
)

def to_representation(self, instance):
    data = super().to_representation(instance)
    if data.get("skills") is None:
        data["skills"] = []
    return data

    # Вложения и служебные поля
    attachments = serializers.SerializerMethodField(read_only=True)
    status = serializers.SerializerMethodField(read_only=True)

    # ↓ поля для каталога
    responses_count = serializers.SerializerMethodField(read_only=True)
    views_count = serializers.SerializerMethodField(read_only=True)
    deadline_text = serializers.SerializerMethodField(read_only=True)

    # Владелец задания — публичные поля (id, username, full_name и т.п.)
    owner = OwnerPublicSerializer(read_only=True, allow_null=True)

    class Meta:
        model = Job
        fields = [
            "id",
            "owner",
            "title",
            "category",
            "description",
            "skills",
            "budget_type",
            "budget_fixed",
            "budget_min",
            "budget_max",
            "deadline",        # исходное поле оставляем
            "deadline_text",   # удобное имя для фронта
            "deadline_type",
            "location",
            "remote",
            "urgent",
            "is_active",
            "created_at",
            "updated_at",
            # счётчики/метрики для каталога:
            "responses_count",
            "views_count",
            # вычисляемые/сервисные:
            "attachments",
            "status",
            "canceled_at",
            "canceled_reason",
        ]
        read_only_fields = [
            "id", "owner", "is_active", "created_at", "updated_at",
            "attachments", "status", "canceled_at", "canceled_reason",
            "responses_count", "views_count", "deadline_text",
        ]

    # ===== Служебные геттеры =====

    def get_status(self, obj: Job) -> str:
        return obj.status

    def get_responses_count(self, obj: Job) -> int:
        """
        Сейчас заглушка/аннотация.
        Если в queryset прилетела аннотация (responses_count / responses_count_annot),
        используем её. Иначе 0.
        """
        return (
            getattr(obj, "responses_count", None)
            or getattr(obj, "responses_count_annot", None)
            or 0
        )

    def get_views_count(self, obj: Job) -> int:
        """
        Аналогично — пока 0, можно заменить на реальный счётчик позже.
        """
        return getattr(obj, "views_count", None) or 0

    def get_deadline_text(self, obj: Job) -> str:
        return obj.deadline or ""

    def get_attachments(self, obj: Job):
        out = []
        atts = getattr(obj, "attachments", None)
        if not atts:
            return out
        for att in atts.all():
            out.append({
                "id": att.id,
                "url": getattr(att, "file_url", None),
                "name": getattr(att, "filename", None),
                "uploaded_at": getattr(att, "uploaded_at", None),
            })
        return out


    # ===== Валидация =====

    def validate(self, attrs):
        title = attrs.get("title", getattr(self.instance, "title", None))
        category = attrs.get("category", getattr(self.instance, "category", None))
        description = attrs.get("description", getattr(self.instance, "description", None))
        budget_type = attrs.get("budget_type", getattr(self.instance, "budget_type", Job.BudgetType.FIXED))
        budget_fixed = attrs.get("budget_fixed", getattr(self.instance, "budget_fixed", None))
        budget_min = attrs.get("budget_min", getattr(self.instance, "budget_min", None))
        budget_max = attrs.get("budget_max", getattr(self.instance, "budget_max", None))

        if not title:
            raise serializers.ValidationError({"title": _("Укажите название задания.")})
        if not category:
            raise serializers.ValidationError({"category": _("Выберите категорию.")})
        if not description or len(description.strip()) < 10:
            raise serializers.ValidationError({"description": _("Опишите задание подробнее (минимум 10 символов).")})

        skills = attrs.get("skills", getattr(self.instance, "skills", []))
        if not isinstance(skills, list):
            raise serializers.ValidationError({"skills": _("Навыки должны быть списком строк.")})
        for s in skills:
            if not isinstance(s, str) or not s.strip():
                raise serializers.ValidationError({"skills": _("Каждый навык должен быть непустой строкой.")})

        if budget_type == Job.BudgetType.FIXED:
            if budget_fixed in (None, ""):
                raise serializers.ValidationError({"budget_fixed": _("Укажите фиксированный бюджет.")})
            try:
                bf = int(budget_fixed)
            except Exception:
                raise serializers.ValidationError({"budget_fixed": _("Бюджет должен быть числом.")})
            if bf <= 0:
                raise serializers.ValidationError({"budget_fixed": _("Бюджет должен быть положительным числом.")})
            attrs["budget_min"] = None
            attrs["budget_max"] = None

        elif budget_type == Job.BudgetType.RANGE:
            if budget_min in (None, "") or budget_max in (None, ""):
                raise serializers.ValidationError({"budget_min": _("Укажите диапазон бюджета (от/до).")})
            try:
                mn = int(budget_min)
                mx = int(budget_max)
            except Exception:
                raise serializers.ValidationError({"budget_min": _("Диапазон бюджета должен быть числом.")})
            if mn <= 0 or mx <= 0:
                raise serializers.ValidationError({"budget_min": _("Значения бюджета должны быть > 0.")})
            if mn > mx:
                raise serializers.ValidationError({"budget_min": _("Минимум не может быть больше максимума.")})
            attrs["budget_fixed"] = None

        else:
            raise serializers.ValidationError({"budget_type": _("Неверный тип бюджета.")})

        return attrs

    # ===== Создание =====

    def create(self, validated_data):
        """
        Проставляем владельца из request.user.
        Создавать может только authenticated customer.
        """
        request = self.context.get("request")
        user = getattr(request, "user", None)

        if not user or not user.is_authenticated:
            raise serializers.ValidationError({"detail": _("Требуется аутентификация.")})

        role = getattr(user, "role", None)
        if role != "customer":
            raise serializers.ValidationError({"detail": _("Создавать задания может только пользователь с ролью заказчик.")})

        validated_data.pop("owner", None)
        validated_data["owner"] = user
        return super().create(validated_data)


class JobAttachmentSerializer(serializers.ModelSerializer):
    # Пишем файл, читаем удобные поля
    file = serializers.FileField(write_only=True)
    url = serializers.SerializerMethodField(read_only=True)
    name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = JobAttachment
        fields = ["id", "job", "file", "url", "name", "uploaded_at"]
        read_only_fields = ["id", "url", "name", "uploaded_at"]

    def get_url(self, obj: JobAttachment):
        return obj.file_url or None

    def get_name(self, obj: JobAttachment):
        return obj.filename

    def create(self, validated_data):
        # Модель сама заполнит original_name и нормализует имя файла
        return super().create(validated_data)
