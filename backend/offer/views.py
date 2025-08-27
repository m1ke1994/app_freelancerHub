from django.shortcuts import render

# Create your views here.
# offer/views.py
from django.db import transaction
from django.db.models import Q
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Proposal, Assignment, ProposalStatus
from .serializers import (
    ProposalCreateSerializer,
    ProposalReadSerializer,
    AssignmentSerializer,
)
from .permissions import (
    IsExecutorForCreate,
    IsProposalExecutorOrJobOwner,
    IsJobOwnerForStatusActions,
    get_job_owner,
)


class ProposalViewSet(viewsets.ModelViewSet):
    """
    /api/proposals/ — CRUD откликов.
    - list/retrieve: читают исполнитель (свои) или владелец job (по ?job=ID).
    - create: только исполнитель; executor берём из request.user.
    - shortlist/accept/reject: только владелец соответствующего job.
    """
    queryset = Proposal.objects.select_related("job", "executor").all()

    def get_serializer_class(self):
        return (
            ProposalReadSerializer
            if self.action in ("list", "retrieve")
            else ProposalCreateSerializer
        )

    def get_permissions(self):
        if self.action in ("shortlist", "accept", "reject"):
            return [permissions.IsAuthenticated(), IsJobOwnerForStatusActions()]
        elif self.action in ("retrieve", "update", "partial_update", "destroy"):
            return [permissions.IsAuthenticated(), IsProposalExecutorOrJobOwner()]
        # list/create по умолчанию
        return [permissions.IsAuthenticated(), IsExecutorForCreate()]

    def get_queryset(self):
        qs = Proposal.objects.select_related("job", "executor")
        user = self.request.user
        if not user or not user.is_authenticated:
            return qs.none()

        job_id = self.request.query_params.get("job")

        # Админам всё
        if getattr(user, "is_staff", False):
            return qs.filter(job_id=job_id) if job_id else qs

        role = getattr(user, "role", None)

        # Заказчик видит отклики только на СВОЁ задание (требуем ?job=)
        if role == "customer":
            if not job_id:
                return qs.none()
            JobModel = Proposal._meta.get_field("job").remote_field.model
            try:
                job = JobModel.objects.get(pk=job_id)
            except JobModel.DoesNotExist:
                raise NotFound("Job not found")
            if get_job_owner(job) != user:
                raise PermissionDenied("Not your job")
            return qs.filter(job_id=job_id)

        # Исполнитель (или если поле role отсутствует) — видит только свои отклики
        return qs.filter(executor=user) if not job_id else qs.filter(executor=user, job_id=job_id)

    # ==== Статусные действия (только владелец job) ====

    @action(detail=True, methods=["post"])
    def shortlist(self, request, pk=None):
        proposal = self.get_object()  # права проверяются в get_permissions
        proposal.status = ProposalStatus.SHORTLISTED
        proposal.save(update_fields=["status", "updated_at"])
        data = ProposalReadSerializer(proposal, context={"request": request}).data
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        proposal = self.get_object()
        proposal.status = ProposalStatus.REJECTED
        proposal.save(update_fields=["status", "updated_at"])
        data = ProposalReadSerializer(proposal, context={"request": request}).data
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def accept(self, request, pk=None):
        proposal = self.get_object()
        with transaction.atomic():
            # 1) помечаем отклик как accepted
            proposal.status = ProposalStatus.ACCEPTED
            proposal.save(update_fields=["status", "updated_at"])
            # 2) создаём/обновляем назначение на задачу (единственность по OneToOne)
            Assignment.objects.update_or_create(
                job=proposal.job,
                defaults={"executor": proposal.executor, "proposal": proposal},
            )
            # 3) (опционально) остальные отклики по задаче — в rejected
            Proposal.objects.filter(job=proposal.job).exclude(pk=proposal.pk).update(
                status=ProposalStatus.REJECTED
            )
        data = ProposalReadSerializer(proposal, context={"request": request}).data
        return Response(data, status=status.HTTP_200_OK)


class AssignmentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    /api/assignments/ — только чтение.
    Видит:
      - назначенный исполнитель (executor),
      - владелец job,
      - staff.
    """
    serializer_class = AssignmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Assignment.objects.select_related("job", "executor", "proposal").all()

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if getattr(user, "is_staff", False):
            return qs
        # назначенный исполнитель
        q = Q(executor=user)

        # владелец job (пытаемся угадать поле владельца — см. permissions.get_job_owner)
        JobModel = Proposal._meta.get_field("job").remote_field.model
        # динамический OR по возможным полям владельца
        owner_q = Q()
        for attr in ("customer", "owner", "user", "author", "created_by", "client"):
            owner_q |= Q(**{f"job__{attr}": user}) | Q(**{f"job__{attr}__user": user})
        q |= owner_q

        return qs.filter(q).distinct()


class StatsView(APIView):
    """
    /api/proposals/stats?job=<id> — счётчики по откликам (для бейджей).
    Доступ: владелец job или staff.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        job_id = request.query_params.get("job")
        if not job_id:
            return Response({"detail": "Parameter 'job' is required."}, status=400)

        JobModel = Proposal._meta.get_field("job").remote_field.model
        try:
            job = JobModel.objects.get(pk=job_id)
        except JobModel.DoesNotExist:
            raise NotFound("Job not found")

        if not (get_job_owner(job) == request.user or getattr(request.user, "is_staff", False)):
            raise PermissionDenied("Not your job")

        qs = Proposal.objects.filter(job_id=job_id)
        data = {
            "job": int(job_id),
            "total": qs.count(),
            "shortlisted": qs.filter(status=ProposalStatus.SHORTLISTED).count(),
            "accepted": qs.filter(status=ProposalStatus.ACCEPTED).count(),
        }
        return Response(data, status=200)
