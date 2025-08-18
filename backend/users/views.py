from rest_framework import permissions
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView
from django.contrib.auth.models import User
from .serializers import RegisterSerializer, UserPublicSerializer

class RegisterView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

class MeView(RetrieveUpdateAPIView):
    serializer_class = UserPublicSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
