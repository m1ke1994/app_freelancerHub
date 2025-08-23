# jobs/views.py
from typing import List

from django.db.models import Prefetch, Q
from django.shortcuts import get_object_or_404

from rest_framework import status, viewsets, permissions, parsers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Job, JobAttachment
from .serializers import JobSerializer, JobAttachmentSerializer


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Разрешает небезопасные операции (PUT/PATCH/DELETE/attach) только владельцу объявления.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return getattr(obj, "owner_id", None) == getattr(request.user, "id", None)


class IsCustomer(permissions.BasePermission):
    """
    Разрешает действие только пользователю с ролью 'customer'.
    Ожидаем, что у модели пользователя есть поле role ('customer' | 'executor').
    """
    message = "Создавать задания может только пользователь с ролью заказчик."

    def has_permission(self, request, view):
        # только для аутентифицированных
        if not request.user or not request.user.is_authenticated:
            return False
        # проверяем роль
        role = getattr(request.user, "role", None)
        return role == "customer"


class JobViewSet(viewsets.ModelViewSet):
    """
    CRUD для заданий:

    - POST /api/jobs/                   — создать задание (ТОЛЬКО customer)
    - GET  /api/jobs/                   — список
    - GET  /api/jobs/{id}/              — детально
    - PATCH/PUT /api/jobs/{id}/         — редактировать (только владелец)
    - DELETE /api/jobs/{id}/            — удалить (только владелец)

    Доп. действия:
    - GET  /api/jobs/{id}/attachments/  — список вложений
    - POST /api/jobs/{id}/attachments/  — загрузить файлы (ТОЛЬКО владелец и customer)
    """
    serializer_class = JobSerializer
    # Базовые парсеры: JSON и multipart (на create/update и upload)
    parser_classes = [parsers.JSONParser, parsers.MultiPartParser, parsers.FormParser]

    def get_queryset(self):
        return (
            Job.objects
            .select_related("owner")
            .prefetch_related(Prefetch("attachments", queryset=JobAttachment.objects.order_by("-uploaded_at")))
            .order_by("-created_at")
        )

    def get_permissions(self):
        """
        - List/Retrieve: доступны всем (чтение).
        - Create: только IsAuthenticated + IsCustomer.
        - Update/PartialUpdate/Delete: IsAuthenticated + IsOwnerOrReadOnly.
        - upload_attachments (POST): IsAuthenticated + IsOwnerOrReadOnly + IsCustomer.
        - list_attachments (GET): доступно всем.
        """
        if self.action in ["list", "retrieve", "list_attachments"]:
            return [permissions.AllowAny()]
        if self.action in ["create"]:
            return [permissions.IsAuthenticated(), IsCustomer()]
        if self.action in ["upload_attachments"]:
            return [permissions.IsAuthenticated(), IsOwnerOrReadOnly(), IsCustomer()]
        # update/partial_update/destroy
        return [permissions.IsAuthenticated(), IsOwnerOrReadOnly()]

    def perform_create(self, serializer):
        # owner проставится в serializer.create(), но DRF вызывает .save() — контекст уже содержит request
        serializer.save()

    def create(self, request, *args, **kwargs):
        """
        Поддерживаем 2 сценария:
        1) JSON без файлов
        2) multipart с полями задания + attachments=<file> (может быть несколько)
        """
        # Явная проверка роли на всякий случай (повтор защитного условия).
        if getattr(request.user, "role", None) != "customer":
            return Response(
                {"detail": "Создавать задания может только пользователь с ролью заказчик."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        job = serializer.save()

        # Вложения (опционально)
        files: List = []
        if "attachments" in request.FILES:
            files = request.FILES.getlist("attachments")
        elif "file" in request.FILES:
            files = [request.FILES["file"]]

        for f in files:
            att_ser = JobAttachmentSerializer(
                data={"job": job.id, "file": f},
                context={"request": request},
            )
            att_ser.is_valid(raise_exception=True)
            att_ser.save()

        headers = self.get_success_headers(serializer.data)
        out = JobSerializer(job, context={"request": request}).data
        return Response(out, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=["get"], url_path="attachments", permission_classes=[permissions.AllowAny])
    def list_attachments(self, request, pk=None):
        job = self.get_object()
        ser = JobAttachmentSerializer(job.attachments.all(), many=True, context={"request": request})
        return Response(ser.data)

    @action(
        detail=True,
        methods=["post"],
        url_path="attachments",
        permission_classes=[permissions.IsAuthenticated, IsOwnerOrReadOnly, IsCustomer],
        parser_classes=[parsers.MultiPartParser, parsers.FormParser],
    )
    def upload_attachments(self, request, pk=None):
        job = self.get_object()
        # Дополнительная защита: право собственности проверяет IsOwnerOrReadOnly
        if job.owner_id != request.user.id:
            return Response({"detail": "Недостаточно прав."}, status=status.HTTP_403_FORBIDDEN)

        files: List = []
        if "attachments" in request.FILES:
            files = request.FILES.getlist("attachments")
        elif "file" in request.FILES:
            files = [request.FILES["file"]]

        if not files:
            return Response({"detail": "Файлы не переданы."}, status=status.HTTP_400_BAD_REQUEST)

        created = []
        for f in files:
            ser = JobAttachmentSerializer(data={"job": job.id, "file": f}, context={"request": request})
            ser.is_valid(raise_exception=True)
            ser.save()
            created.append(ser.data)

        return Response(created, status=status.HTTP_201_CREATED)


class JobAttachmentDetail(APIView):
    """
    Удаление конкретного вложения (только владелец задания и только customer).
    DELETE /api/jobs/attachments/<id>/
    """
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk: int):
        att = get_object_or_404(JobAttachment.objects.select_related("job"), pk=pk)
        if getattr(request.user, "role", None) != "customer":
            return Response(
                {"detail": "Удалять вложения может только заказчик."},
                status=status.HTTP_403_FORBIDDEN
            )
        if att.job.owner_id != request.user.id:
            return Response({"detail": "Недостаточно прав."}, status=status.HTTP_403_FORBIDDEN)
        att.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
