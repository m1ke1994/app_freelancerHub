from rest_framework.permissions import BasePermission, SAFE_METHODS

# Возможные имена поля владельца у Job
JOB_OWNER_ATTRS = ["owner", "customer", "user", "author", "created_by", "client"]


def get_job_owner(job):
    """
    Возвращаем реального пользователя-владельца задания:
    job.owner / job.customer / job.user / job.author / job.created_by / job.client.
    Если это профиль/модель с полем user — вернём .user
    """
    for attr in JOB_OWNER_ATTRS:
        if hasattr(job, attr):
            candidate = getattr(job, attr)
            # если это профиль с .user
            if hasattr(candidate, "user"):
                return getattr(candidate, "user")
            return candidate
    return None


class IsExecutorForCreate(BasePermission):
    """
    Разрешение на создание и просмотр списка собственных откликов.
    Создавать может любой аутентифицированный, но НЕ владелец job.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        # читать список/создавать — проверяется на уровне viewset get_queryset
        return True


class IsProposalExecutorOrJobOwner(BasePermission):
    """
    Доступ к retrieve/update/destroy: либо исполнитель-автор отклика, либо владелец job.
    """
    def has_object_permission(self, request, view, obj):
        if not (request.user and request.user.is_authenticated):
            return False
        is_executor_owner = obj.executor_id == request.user.id
        job_owner = get_job_owner(obj.job)
        is_job_owner = job_owner == request.user

        if request.method in SAFE_METHODS:
            return is_executor_owner or is_job_owner

        # менять/удалять отклик может только исполнитель-автор
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
