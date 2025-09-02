from rest_framework import serializers
from .models import Proposal, Assignment, ProposalStatus
from .permissions import get_job_owner


class ProposalCreateSerializer(serializers.ModelSerializer):
    """Создание/редактирование отклика исполнителем."""
    class Meta:
        model = Proposal
        fields = ["id", "job", "cover_letter", "bid_amount", "days"]

    def validate(self, attrs):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        job = attrs.get("job")

        if not user or not user.is_authenticated:
            raise serializers.ValidationError("Auth required")

        # нельзя откликаться на собственное задание
        owner = get_job_owner(job)
        if owner and owner == user:
            raise serializers.ValidationError("Нельзя откликаться на собственное задание")

        # нельзя задублировать отклик
        if Proposal.objects.filter(job=job, executor=user).exists():
            raise serializers.ValidationError("Вы уже отправили отклик на это задание")

        return attrs

    def create(self, validated_data):
        user = self.context["request"].user
        return Proposal.objects.create(executor=user, **validated_data)

    def update(self, instance, validated_data):
        # редактировать может только автор-исполнитель (проверяется в permissions)
        for field in ["cover_letter", "bid_amount", "days"]:
            if field in validated_data:
                setattr(instance, field, validated_data[field])
        instance.save()
        return instance


class ExecutorMiniSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    full_name = serializers.CharField(allow_null=True, required=False)
    avatar_url = serializers.CharField(allow_null=True, required=False)
    rating = serializers.FloatField(allow_null=True, required=False)

    @staticmethod
    def from_user(u):
        full_name = None
        # Поддержка first_name/last_name или profile.full_name
        if getattr(u, "first_name", None) or getattr(u, "last_name", None):
            full_name = f"{getattr(u,'first_name','').strip()} {getattr(u,'last_name','').strip()}".strip() or None
        if not full_name and hasattr(u, "profile") and getattr(u.profile, "full_name", None):
            full_name = u.profile.full_name

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


class ProposalReadSerializer(serializers.ModelSerializer):
    executor = serializers.SerializerMethodField()

    class Meta:
        model = Proposal
        fields = [
            "id",
            "job",
            "executor",
            "cover_letter",
            "bid_amount",
            "days",
            "status",
            "created_at",
            "updated_at",
        ]

    def get_executor(self, obj):
        return ExecutorMiniSerializer.from_user(obj.executor)


class ProposalStatusSerializer(serializers.ModelSerializer):
    """Изменение статуса отклика работодателем (короткий список/акцепт/отклонение)."""
    class Meta:
        model = Proposal
        fields = ["id", "status"]
        read_only_fields = ["id"]

    def validate_status(self, value):
        if value not in {
            ProposalStatus.SHORTLISTED,
            ProposalStatus.ACCEPTED,
            ProposalStatus.REJECTED,
            ProposalStatus.WITHDRAWN,
        }:
            raise serializers.ValidationError("Недопустимый статус")
        return value


class AssignmentReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = ["id", "job", "executor", "proposal", "created_at"]
