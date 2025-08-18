from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Task, Service
from .serializers import TaskSerializer, ServiceSerializer

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all().order_by("-created_at")
    serializer_class = TaskSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["status", "category"]
    search_fields = ["title", "description", "location"]
    ordering_fields = ["created_at", "price"]

class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all().order_by("-created_at")
    serializer_class = ServiceSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["category", "rate_type"]
    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "hourly_rate", "project_rate"]
