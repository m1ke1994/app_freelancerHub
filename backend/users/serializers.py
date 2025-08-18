# users/serializers.py
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from rest_framework import serializers, exceptions
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

phone_validator = RegexValidator(
    regex=r'^\+7\d{10}$',
    message='Телефон должен быть в формате +7XXXXXXXXXX (10 цифр после +7).'
)

class RegisterSerializer(serializers.ModelSerializer):
    confirm = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=User.ROLE_CHOICES)
    phone = serializers.CharField(validators=[phone_validator])
    class Meta:
        model = User
        fields = ("first_name","last_name","email","phone","role","password","confirm")
        extra_kwargs = {
            "first_name": {"required": True, "allow_blank": False},
            "last_name": {"required": True, "allow_blank": False},
            "password": {"write_only": True},
            "email": {"required": True, "allow_blank": False},
            "phone": {"required": True, "allow_blank": False},
        }
    def validate_email(self, value: str) -> str:
        email = (value or "").strip().lower()
        if not email:
            raise serializers.ValidationError("E-mail обязателен")
        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError("Пользователь с таким e-mail уже существует")
        return email
    def validate_phone(self, value: str) -> str:
        phone = (value or "").strip()
        if User.objects.filter(phone=phone).exists():
            raise serializers.ValidationError("Пользователь с таким телефоном уже существует")
        return phone
    def validate(self, attrs):
        if attrs.get("password") != attrs.get("confirm"):
            raise serializers.ValidationError({"confirm": "Пароли не совпадают"})
        return attrs
    def create(self, validated_data):
        validated_data.pop("confirm", None)
        password = validated_data.pop("password")
        email = validated_data["email"].lower().strip()
        user = User(
            username=email,
            email=email,
            first_name=validated_data.get("first_name", "").strip(),
            last_name=validated_data.get("last_name", "").strip(),
            phone=validated_data["phone"],
            role=validated_data["role"],
        )
        user.set_password(password)
        user.save()
        return user

class ProfileSerializer(serializers.ModelSerializer):
    avatar_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        # отдадим и примем все поля анкеты + системные read-only
        fields = (
            "id","email","phone","role","username",
            "first_name","last_name",
            "avatar_url",

            # анкета
            "title","bio","location","gender","education","status",
            "categories","skills",
            "rate_type","hourly_rate","project_rate","availability",
            "links","socials","portfolio","busy_dates",
        )
        read_only_fields = ("id","email","phone","role","username","avatar_url")

    def get_avatar_url(self, obj):
        url = getattr(obj, "avatar_url", None)
        request = self.context.get("request")
        if url and request is not None and not str(url).startswith("http"):
            return request.build_absolute_uri(url)
        return url

class AvatarUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("avatar",)

class EmailTokenObtainPairSerializer(serializers.Serializer):
    username = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField(write_only=True)
    def validate(self, attrs):
        username = (attrs.get("username") or "").strip()
        email = (attrs.get("email") or "").strip().lower()
        password = attrs.get("password") or ""
        if not (email or username):
            raise exceptions.ValidationError({
                "email": "Укажите e-mail",
                "username": "Укажите username или e-mail",
            })
        user = None
        if email:
            user = User.objects.filter(email__iexact=email).first()
        if user is None and username:
            user = User.objects.filter(username__iexact=username).first()
        if user is None:
            raise exceptions.ValidationError({"email": "Пользователь не найден"})
        if not user.check_password(password):
            raise exceptions.ValidationError({"password": "Неверный пароль"})
        if not user.is_active:
            raise exceptions.ValidationError({"detail": "Аккаунт отключён. Обратитесь в поддержку."})
        refresh = RefreshToken.for_user(user)
        return {"access": str(refresh.access_token), "refresh": str(refresh)}
