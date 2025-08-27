# offer/models.py
from django.conf import settings
from django.db import models


class ProposalStatus(models.TextChoices):
    SENT = "sent", "Sent"
    WITHDRAWN = "withdrawn", "Withdrawn"
    SHORTLISTED = "shortlisted", "Shortlisted"
    ACCEPTED = "accepted", "Accepted"
    REJECTED = "rejected", "Rejected"


class Proposal(models.Model):
    # ⚠️ Если у тебя модель задания называется иначе (например, tasks.Task),
    # замени "jobs.Job" на "<app_label>.<ModelName>"
    job = models.ForeignKey("jobs.Job", on_delete=models.CASCADE, related_name="proposals")
    executor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="proposals")

    cover_letter = models.TextField()
    bid_amount = models.DecimalField(max_digits=12, decimal_places=2)
    days = models.PositiveIntegerField(null=True, blank=True)

    status = models.CharField(max_length=20, choices=ProposalStatus.choices, default=ProposalStatus.SENT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["job", "executor"], name="uniq_offer_job_executor"),
        ]
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["job"]),
            models.Index(fields=["executor"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"Proposal#{self.pk} job={self.job_id} executor={self.executor_id} status={self.status}"


class Assignment(models.Model):
    # единственное назначение на задачу
    job = models.OneToOneField("jobs.Job", on_delete=models.CASCADE, related_name="assignment")
    executor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="assignments")
    proposal = models.OneToOneField("offer.Proposal", on_delete=models.CASCADE, related_name="assignment")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Assignment job={self.job_id} -> executor={self.executor_id}"
