# jobs/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import JobViewSet, JobAttachmentDetail

router = DefaultRouter()
router.register(r'', JobViewSet, basename='job')

urlpatterns = [
    path('', include(router.urls)),
    # удаление конкретного вложения
    path('attachments/<int:pk>/', JobAttachmentDetail.as_view(), name='job-attachment-detail'),
]
