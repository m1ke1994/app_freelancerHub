# offer/permissions.py
from rest_framework.permissions import BasePermission, SAFE_METHODS

# Если владелец задания называется иначе — впиши в список нужные варианты
JOB_OWNER_ATTRS = ["customer", "owner", "user", "author", "created_by", "client"]


def get_job_owner(job):
    """
    Пытаемся определить владельца задания максимально мягко:
    job.customer / job.owner / job.user / job.author / job.created_by / job.client.
    Если это профиль с полем user — вернём user.
    """
    for attr in JOB_OWNER_ATTRS:
        if hasattr(job, attr):
            candidate = getattr(job, attr)
            if candidate is None:
                continue
            # если это профиль с user внутри
            if hasattr(candidate, "user"):
                return getattr(candidate, "user")
            return candidate
    return None


def is_executor(user):
    """
    Роль исполнителя. Если поле role отсутствует — считаем, что проверка роли не применяется,
    и решает остальная логика (но пользователь должен быть аутентифицирован).
    """
    role = getattr(user, "role", None)
    return (role is None) or (role == "executor")


class IsExecutorForCreate(BasePermission):
    """
    POST /api/... — только для аутентифицированных пользователей с ролью executor (если поле есть).
    Чтение (GET/HEAD/OPTIONS) — достаточно быть аутентифицированным (фильтруем в queryset).
    """
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.method in SAFE_METHODS:
            return True
        if request.method == "POST":
            return is_executor(request.user)
        # PUT/PATCH/DELETE зарезервируем под объектные правила (ниже)
        return True


class IsProposalExecutorOrJobOwner(BasePermission):
    """
    Объектные права: читать может исполнитель отклика или владелец задания.
    Редактировать/удалять отклик — только его исполнитель.
    """
    def has_object_permission(self, request, view, obj):
        if not (request.user and request.user.is_authenticated):
            return False

        is_executor_owner = (obj.executor_id == request.user.id)
        job_owner = get_job_owner(obj.job)
        is_job_owner = (job_owner == request.user)

        if request.method in SAFE_METHODS:
            return is_executor_owner or is_job_owner

        # Изменять содержимое отклика (PUT/PATCH/DELETE) — только сам исполнитель
        return is_executor_owner


class IsJobOwnerForStatusActions(BasePermission):
    """
    Для кастомных действий (shortlist/accept/reject): только владелец соответствующего job.
    """
    def has_object_permission(self, request, view, obj):
        if not (request.user and request.user.is_authenticated):
            return False
        job_owner = get_job_owner(obj.job)
        return job_owner == request.user
