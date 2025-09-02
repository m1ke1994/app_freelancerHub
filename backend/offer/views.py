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
    ProposalStatusSerializer,
    AssignmentReadSerializer,
)
from .permissions import (
    IsExecutorForCreate,
    IsProposalExecutorOrJobOwner,
    IsJobOwnerForStatusActions,
    get_job_owner,
)


class ProposalViewSet(viewsets.ModelViewSet):
    """
    list:    Исполнитель — свои отклики; Владелец job — отклики на его задания (через ?job=<id> или ?mine=1)
    create:  Исполнитель создаёт отклик
    retrieve/update/destroy: исполнитель-автор; читать также может владелец job
    """
    queryset = Proposal.objects.select_related("job", "executor")
    serializer_class = ProposalReadSerializer

    def get_permissions(self):
        if self.action in ("shortlist", "accept", "reject"):
            return [permissions.IsAuthenticated(), IsJobOwnerForStatusActions()]
        elif self.action in ("retrieve", "update", "partial_update", "destroy"):
            return [permissions.IsAuthenticated(), IsProposalExecutorOrJobOwner()]
        # list/create по умолчанию
        return [permissions.IsAuthenticated(), IsExecutorForCreate()]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if not user or not user.is_authenticated:
            return qs.none()

        job_id = self.request.query_params.get("job")
        mine = self.request.query_params.get("mine")
        # Если передан ?job=<id> и текущий пользователь — владелец этого job, вернём все отклики на него
        if job_id:
            try:
                JobModel = qs.model._meta.get_field("job").remote_field.model  # jobs.Job
                job = JobModel.objects.select_related().get(pk=job_id)
            except JobModel.DoesNotExist:
                return qs.none()
            if get_job_owner(job) == user:
                return qs.filter(job_id=job_id)
            else:
                # не владелец — видит только свой отклик (если есть)
                return qs.filter(job_id=job_id, executor=user)

        # ?mine=1 — для владельца: все отклики на его задания
        if mine:
            # найдём все его job_ids
            JobModel = qs.model._meta.get_field("job").remote_field.model
            job_ids = list(JobModel.objects.filter(
                Q(owner=user) | Q(customer=user) | Q(user=user) | Q(author=user) | Q(created_by=user) | Q(client=user)
            ).values_list("id", flat=True))
            return qs.filter(job_id__in=job_ids)

        # по умолчанию исполнитель видит только свои отклики
        return qs.filter(executor=user)

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return ProposalCreateSerializer
        return super().get_serializer_class()

    def perform_create(self, serializer):
        serializer.save()  # executor подставится в serializer.create()

    @action(detail=True, methods=["POST"])
    def shortlist(self, request, pk=None):
        proposal = self.get_object()
        # проверка владельца job — в IsJobOwnerForStatusActions
        proposal.status = ProposalStatus.SHORTLISTED
        proposal.save(update_fields=["status", "updated_at"])
        return Response(ProposalReadSerializer(proposal).data)

    @action(detail=True, methods=["POST"])
    def reject(self, request, pk=None):
        proposal = self.get_object()
        proposal.status = ProposalStatus.REJECTED
        proposal.save(update_fields=["status", "updated_at"])
        return Response(ProposalReadSerializer(proposal).data)

    @action(detail=True, methods=["POST"])
    def accept(self, request, pk=None):
        """
        Акцепт отклика: создаём Assignment (единственный на job), ставим статус ACCEPTED.
        """
        proposal = self.get_object()
        job = proposal.job

        # только владелец job
        if get_job_owner(job) != request.user:
            raise PermissionDenied("Not your job")

        with transaction.atomic():
            # Один assignment на задачу
            Assignment.objects.filter(job=job).delete()
            assignment = Assignment.objects.create(
                job=job,
                executor=proposal.executor,
                proposal=proposal,
            )
            proposal.status = ProposalStatus.ACCEPTED
            proposal.save(update_fields=["status", "updated_at"])
        return Response(
            {
                "proposal": ProposalReadSerializer(proposal).data,
                "assignment": AssignmentReadSerializer(assignment).data,
            },
            status=status.HTTP_200_OK,
        )


class AssignmentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Assignment.objects.select_related("job", "executor", "proposal")
    serializer_class = AssignmentReadSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if not user or not user.is_authenticated:
            return qs.none()
        # исполнитель видит свои назначения, владелец job — назначения по его задачам
        return qs.filter(
            Q(executor=user) |
            Q(job__owner=user) | Q(job__customer=user) | Q(job__user=user) |
            Q(job__author=user) | Q(job__created_by=user) | Q(job__client=user)
        )


class StatsView(APIView):
    """
    GET /api/proposals/stats?job=<id> — агрегаты по откликам для конкретной задачи
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        job_id = request.query_params.get("job")
        if not job_id:
            return Response({"detail": "job is required"}, status=400)

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
