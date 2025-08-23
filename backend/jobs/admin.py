# jobs/admin.py
from django.contrib import admin
from .models import Job, JobAttachment


class JobAttachmentInline(admin.TabularInline):
    model = JobAttachment
    extra = 0
    readonly_fields = ["uploaded_at", "original_name", "file"]
    fields = ["original_name", "file", "uploaded_at"]


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = (
        "id", "title", "category", "owner", "budget_type",
        "budget_fixed", "budget_min", "budget_max",
        "urgent", "remote", "is_active", "created_at"
    )
    list_filter = ("category", "urgent", "remote", "is_active", "budget_type", "created_at")
    search_fields = ("title", "description", "location", "owner__email")
    inlines = [JobAttachmentInline]
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (None, {
            "fields": ("owner", "title", "category", "description", "skills")
        }),
        ("Бюджет и сроки", {
            "fields": ("budget_type", "budget_fixed", "budget_min", "budget_max",
                       "deadline", "deadline_type")
        }),
        ("Прочее", {
            "fields": ("location", "remote", "urgent", "is_active")
        }),
        ("Служебное", {
            "fields": ("created_at", "updated_at")
        }),
    )


@admin.register(JobAttachment)
class JobAttachmentAdmin(admin.ModelAdmin):
    list_display = ("id", "job", "original_name", "uploaded_at")
    search_fields = ("original_name", "job__title")
    readonly_fields = ("uploaded_at",)
