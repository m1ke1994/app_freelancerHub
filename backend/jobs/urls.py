# jobs/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.views import APIView
from rest_framework.response import Response

from .views import JobViewSet, JobAttachmentDetail
from .models import Job

router = DefaultRouter()
# /api/jobs/ , /api/jobs/{id}/ , /api/jobs/{id}/attachments/
router.register(r"", JobViewSet, basename="jobs")


class JobCategories(APIView):
    """
    GET /api/jobs/categories/
    Возвращает список доступных категорий из Job.CATEGORIES.
    """
    def get(self, request):
        return Response([c[0] for c in Job.CATEGORIES])


urlpatterns = [
    path("categories/", JobCategories.as_view(), name="job-categories"),
    path("", include(router.urls)),
    # Удаление конкретного вложения: DELETE /api/jobs/attachments/{pk}/
    path("attachments/<int:pk>/", JobAttachmentDetail.as_view(), name="job-attachment-detail"),
]
