# users/views.py
from django.db import IntegrityError
from django.contrib.auth import get_user_model
from rest_framework import status, permissions, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser

from .serializers import (
    RegisterSerializer,
    ProfileSerializer,
    AvatarUploadSerializer,
    EmailTokenObtainPairSerializer,
)
from .throttles import LoginRateThrottle

User = get_user_model()

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = serializer.save()
        except IntegrityError as e:
            msg = "Пользователь с такими данными уже существует."
            if "email" in str(e).lower():
                msg = "Пользователь с таким email уже существует."
            if "phone" in str(e).lower():
                msg = "Пользователь с таким телефоном уже существует."
            return Response({"detail": msg}, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            {"id": user.id, "email": user.email, "phone": user.phone, "role": user.role},
            status=status.HTTP_201_CREATED,
        )

class ProfileView(generics.RetrieveUpdateAPIView):
    """
    GET /api/accounts/profile/
    PATCH /api/accounts/profile/
    """
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_object(self):
        return self.request.user
    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx

class AvatarUploadView(generics.UpdateAPIView):
    serializer_class = AvatarUploadSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    def get_object(self):
        return self.request.user
    def patch(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        profile = ProfileSerializer(user, context={"request": request})
        return Response(profile.data, status=status.HTTP_200_OK)
    def put(self, request, *args, **kwargs):
        return self.patch(request, *args, **kwargs)

class EmailTokenObtainPairView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [LoginRateThrottle]
    def post(self, request, *args, **kwargs):
        serializer = EmailTokenObtainPairSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)
