from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TaskViewSet, ServiceViewSet

router = DefaultRouter()
router.register(r"tasks", TaskViewSet, basename="task")
router.register(r"services", ServiceViewSet, basename="service")

urlpatterns = [
    path("", include(router.urls)),
]
