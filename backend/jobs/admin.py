# jobs/admin.py
from django.contrib import admin, messages
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from .models import Job, JobAttachment


# ======= Inlines =======

class JobAttachmentInline(admin.TabularInline):
    model = JobAttachment
    extra = 0
    can_delete = True
    readonly_fields = ("uploaded_at", "original_name", "file_link")
    fields = ("original_name", "file", "file_link", "uploaded_at")

    def file_link(self, obj):
        if obj and obj.file and hasattr(obj.file, "url"):
            return format_html('<a href="{}" target="_blank">Открыть</a>', obj.file.url)
        return "—"

    file_link.short_description = "Ссылка"


# ======= List Filter по статусу =======

class JobStatusListFilter(admin.SimpleListFilter):
    title = "Статус"
    parameter_name = "status"

    def lookups(self, request, model_admin):
        return (
            ("active", "Активно"),
            ("archived", "Архив (отменено)"),
        )

    def queryset(self, request, queryset):
        val = self.value()
        if val == "active":
            return queryset.filter(is_active=True)
        if val == "archived":
            return queryset.filter(is_active=False)
        return queryset


# ======= Admin: Job =======

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    # колонки списка
    list_display = (
        "id",
        "title",
        "category",
        "owner_display",
        "status_badge",
        "budget_summary",
        "urgent",
        "remote",
        "attachments_count",
        "created_at",
    )
    list_display_links = ("id", "title")

    # фильтры и поиск
    list_filter = (
        JobStatusListFilter,
        "category",
        "urgent",
        "remote",
        "budget_type",
        "deadline_type",
        "created_at",
    )
    search_fields = ("title", "description", "location", "owner__email")
    date_hierarchy = "created_at"
    ordering = ("-created_at",)

    # поля только для чтения
    readonly_fields = ("created_at", "updated_at", "status_readonly", "canceled_at", "canceled_reason")

    # инлайны
    inlines = [JobAttachmentInline]

    # группировка полей на форме
    fieldsets = (
        (None, {
            "fields": ("owner", "title", "category", "description", "skills")
        }),
        ("Бюджет", {
            "fields": ("budget_type", "budget_fixed", "budget_min", "budget_max")
        }),
        ("Сроки", {
            "fields": ("deadline", "deadline_type")
        }),
        ("Размещение", {
            "fields": ("location", "remote", "urgent")
        }),
        ("Статус/Отмена", {
            "fields": ("status_readonly", "is_active", "canceled_at", "canceled_reason")
        }),
        ("Служебное", {
            "fields": ("created_at", "updated_at")
        }),
    )

    # оптимизация запросов
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("owner").prefetch_related("attachments")

    # ==== Колонки/представления ====

    def owner_display(self, obj: Job):
        # Показать почту/ID владельца
        email = getattr(obj.owner, "email", None) or f"id={obj.owner_id}"
        return email
    owner_display.short_description = "Владелец"

    def status_badge(self, obj: Job):
        if obj.is_active:
            return format_html(
                '<span style="padding:2px 6px;border:1px solid #fbbf24;border-radius:9999px;background:#fef3c7;color:#92400e;font-size:12px;">Активно</span>'
            )
        # Архив: показать причину/дату во всплывающей подсказке
        tip = obj.canceled_reason or ""
        date_str = obj.canceled_at.strftime("%Y-%m-%d %H:%M") if obj.canceled_at else ""
        title = f"{date_str} {tip}".strip()
        return format_html(
            '<span title="{}" style="padding:2px 6px;border:1px solid #cbd5e1;border-radius:9999px;background:#f1f5f9;color:#334155;font-size:12px;">Архив</span>',
            title
        )
    status_badge.short_description = "Статус"
    status_badge.admin_order_field = "is_active"

    def status_readonly(self, obj: Job):
        # read-only поле в форме
        return "Активно" if obj and obj.is_active else "Архив (отменено)"
    status_readonly.short_description = "Текущий статус"

    def budget_summary(self, obj: Job):
        if obj.budget_type == Job.BudgetType.FIXED:
            if obj.budget_fixed:
                return f"Фикс: {obj.budget_fixed:,} ₽".replace(",", " ")
            return "Фикс: —"
        # RANGE
        if obj.budget_min and obj.budget_max:
            return f"Диапазон: {obj.budget_min:,}–{obj.budget_max:,} ₽".replace(",", " ")
        return "Диапазон: —"
    budget_summary.short_description = "Бюджет"
    budget_summary.admin_order_field = "budget_type"

    def attachments_count(self, obj: Job):
        cnt = getattr(obj, "attachments", []).count() if hasattr(obj, "attachments") else obj.attachments.count()
        return cnt
    attachments_count.short_description = "Файлы"

    # ======= Actions =======

    @admin.action(description="Отменить выбранные задания (в архив)")
    def cancel_selected(self, request, queryset):
        updated = 0
        now = timezone.now()
        for job in queryset.filter(is_active=True):
            job.is_active = False
            if not job.canceled_at:
                job.canceled_at = now
            job.save(update_fields=["is_active", "canceled_at", "updated_at"])
            updated += 1
        if updated:
            self.message_user(request, _(f"Переведено в архив: {updated}"), level=messages.SUCCESS)
        else:
            self.message_user(request, _("Нет активных заданий для архивации."), level=messages.WARNING)

    @admin.action(description="Вернуть из архива (сделать активными)")
    def restore_selected(self, request, queryset):
        updated = queryset.filter(is_active=False).update(is_active=True)
        if updated:
            self.message_user(request, _(f"Восстановлено из архива: {updated}"), level=messages.SUCCESS)
        else:
            self.message_user(request, _("Нечего восстанавливать."), level=messages.WARNING)

    actions = ("cancel_selected", "restore_selected",)


# ======= Admin: JobAttachment =======

@admin.register(JobAttachment)
class JobAttachmentAdmin(admin.ModelAdmin):
    list_display = ("id", "job_link", "original_name", "file_link", "uploaded_at")
    list_select_related = ("job",)
    search_fields = ("original_name", "job__title")
    readonly_fields = ("uploaded_at", "file_link")
    fields = ("job", "original_name", "file", "file_link", "uploaded_at")
    date_hierarchy = "uploaded_at"
    ordering = ("-uploaded_at",)

    def job_link(self, obj):
        return format_html('<a href="/admin/jobs/job/{}/change/">{}</a>', obj.job_id, obj.job)
    job_link.short_description = "Задание"

    def file_link(self, obj):
        if obj and obj.file and hasattr(obj.file, "url"):
            return format_html('<a href="{}" target="_blank">Открыть</a>', obj.file.url)
        return "—"
    file_link.short_description = "Ссылка"
