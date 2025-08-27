# offer/serializers.py
from rest_framework import serializers
from .models import Proposal, Assignment, ProposalStatus


class ProposalCreateSerializer(serializers.ModelSerializer):
    """Создание/редактирование отклика исполнителем."""
    class Meta:
        model = Proposal
        fields = ["id", "job", "cover_letter", "bid_amount", "days"]

    def validate(self, attrs):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        job = attrs.get("job")

        # роль (мягкая проверка, не падаем, если поля нет)
        role = getattr(user, "role", None)
        if role and role != "executor":
            raise serializers.ValidationError("Отклик может отправить только исполнитель.")

        # запрет повторного отклика
        if user and job and Proposal.objects.filter(job=job, executor=user).exists():
            raise serializers.ValidationError("Вы уже отправили отклик на это задание.")

        return attrs

    def create(self, validated_data):
        request = self.context.get("request")
        validated_data["executor"] = request.user
        # статус по умолчанию — sent
        validated_data.setdefault("status", ProposalStatus.SENT)
        return super().create(validated_data)


class ProposalReadSerializer(serializers.ModelSerializer):
    """Чтение отклика. Вложенно возвращаем публичные поля исполнителя."""
    executor = serializers.SerializerMethodField()

    class Meta:
        model = Proposal
        fields = [
            "id", "job",
            "executor",
            "cover_letter", "bid_amount", "days",
            "status", "created_at", "updated_at",
        ]

    def get_executor(self, obj):
        u = obj.executor
        # аккуратно собираем ФИО или username
        first = getattr(u, "first_name", "") or ""
        last = getattr(u, "last_name", "") or ""
        full_name = (f"{first} {last}").strip() or getattr(u, "username", str(u.pk))

        # аватар: поддержка avatar_url (str) или avatar (FileField/ImageField)
        avatar_attr = getattr(u, "avatar_url", None) or getattr(u, "avatar", None)
        if hasattr(avatar_attr, "url"):
            avatar_url = avatar_attr.url
        else:
            avatar_url = avatar_attr if isinstance(avatar_attr, str) else None

        rating = getattr(u, "rating", None)

        return {
            "id": u.pk,
            "full_name": full_name,
            "avatar_url": avatar_url,
            "rating": rating,
        }


class AssignmentSerializer(serializers.ModelSerializer):
    """Чтение назначения (кто принят на задачу)."""
    executor = serializers.SerializerMethodField()

    class Meta:
        model = Assignment
        fields = ["id", "job", "executor", "proposal", "created_at"]

    def get_executor(self, obj):
        u = obj.executor
        first = getattr(u, "first_name", "") or ""
        last = getattr(u, "last_name", "") or ""
        full_name = (f"{first} {last}").strip() or getattr(u, "username", str(u.pk))

        avatar_attr = getattr(u, "avatar_url", None) or getattr(u, "avatar", None)
        if hasattr(avatar_attr, "url"):
            avatar_url = avatar_attr.url
        else:
            avatar_url = avatar_attr if isinstance(avatar_attr, str) else None

        rating = getattr(u, "rating", None)

        return {
            "id": u.pk,
            "full_name": full_name,
            "avatar_url": avatar_url,
            "rating": rating,
        }
