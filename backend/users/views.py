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
    EmailTokenObtainPairSerializer,   # логин по email/username
    PublicProfileUpdateSerializer,     # ← добавлено: PATCH анкеты
)
from .throttles import LoginRateThrottle  # ограничение частоты логина

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
            # Уникальность email/phone
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
    GET  /api/accounts/profile/   -> профиль текущего пользователя.
    PATCH /api/accounts/profile/  -> обновление публичной анкеты (JSON),
                                     отвечает обновлённым профилем (ProfileSerializer).
    """
    permission_classes = [permissions.IsAuthenticated]

    # GET: используем сериализатор чтения
    def get_serializer_class(self):
        if self.request.method in ("PATCH", "PUT"):
            return PublicProfileUpdateSerializer
        return ProfileSerializer

    def get_object(self):
        return self.request.user

    # чтобы ProfileSerializer мог собрать абсолютный avatar_url
    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx

    # Переопределяем PATCH, чтобы всегда возвращать полный профиль
    def patch(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = PublicProfileUpdateSerializer(
            instance=user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()  # сохранит только существующие в модели поля
        # возвращаем полный профиль
        profile = ProfileSerializer(user, context={"request": request})
        return Response(profile.data, status=status.HTTP_200_OK)

    # На случай PUT — ведём себя как PATCH
    def put(self, request, *args, **kwargs):
        return self.patch(request, *args, **kwargs)


class AvatarUploadView(generics.UpdateAPIView):
    """
    PATCH /api/accounts/profile/avatar/
    Body: multipart/form-data с полем "avatar".
    Отдаёт тот же профиль (как ProfileView), чтобы фронту было удобно сразу перерисовать.
    """
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
        # отдадим полный профиль
        profile = ProfileSerializer(user, context={"request": request})
        return Response(profile.data, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        return self.patch(request, *args, **kwargs)


class EmailTokenObtainPairView(APIView):
    """
    POST /api/accounts/token/  -> { "access": "...", "refresh": "..." }
    Принимает:
      - { "email": "...", "password": "..." }   ИЛИ
      - { "username": "...", "password": "..." }
    username у нас = email, так что фронт может продолжать слать {username: email}.
    """
    permission_classes = [permissions.AllowAny]
    throttle_classes = [LoginRateThrottle]

    def post(self, request, *args, **kwargs):
        serializer = EmailTokenObtainPairSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)
