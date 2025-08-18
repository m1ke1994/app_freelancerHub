from django.db import IntegrityError
from django.contrib.auth import get_user_model
from rest_framework import status, permissions, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import RegisterSerializer, ProfileSerializer

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


class ProfileView(generics.RetrieveAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


# JWT:
# POST /api/accounts/token/  -> {access, refresh}
# (по умолчанию использует username+password; username у нас = email)
class LoginView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]
