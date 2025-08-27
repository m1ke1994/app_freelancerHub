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
        fields = ("first_name", "last_name", "email", "phone", "role", "password", "confirm")
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
            "id", "email", "phone", "role", "username",
            "first_name", "last_name",
            "avatar_url",

            # анкета
            "title", "bio", "location", "gender", "education", "status",
            "categories", "skills",
            "rate_type", "hourly_rate", "project_rate", "availability",
            "links", "socials", "portfolio", "busy_dates",
        )
        read_only_fields = ("id", "email", "phone", "role", "username", "avatar_url")

    def get_avatar_url(self, obj):
        """
        Возвращаем абсолютный URL аватара, если он есть.
        Не обращаемся к .url, пока не проверим, что имя файла задано.
        """
        # 1) если в модели есть вычисляемое поле/свойство avatar_url — используем его
        url = getattr(obj, "avatar_url", None)

        # 2) иначе пытаемся взять из ImageFieldFile, но ТОЛЬКО если есть имя
        if not url:
            avatar = getattr(obj, "avatar", None)
            # безопасно проверяем имя файла
            if avatar is not None and getattr(avatar, "name", ""):
                try:
                    url = avatar.url  # здесь уже безопасно пробуем .url
                except Exception:
                    url = None

        # 3) делаем абсолютный URL при наличии request
        request = self.context.get("request")
        if url and request is not None and not str(url).startswith("http"):
            return request.build_absolute_uri(url)
        return url


class AvatarUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("avatar",)

    def validate_avatar(self, file):
        if not file:
            raise serializers.ValidationError("Файл не передан.")
        ctype = getattr(file, "content_type", "") or ""
        if ctype and not ctype.startswith("image/"):
            raise serializers.ValidationError("Загрузите изображение (PNG/JPG).")
        if file.size and file.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("Слишком большой файл (макс 5 МБ).")
        return file


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


# === Публичный сериализатор владельца задания (для вложения в jobs) ===
class OwnerPublicSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    avatar_url = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "full_name",
            "avatar_url",  # получаем из avatar_url или avatar.url
            "rating",      # float, 0.0 если нет поля
        )
        read_only_fields = fields

    def get_full_name(self, obj):
        name = f"{(obj.first_name or '').strip()} {(obj.last_name or '').strip()}".strip()
        return name or None

    def get_avatar_url(self, obj):
        """
        Безопасно получаем URL аватара.
        Никогда не обращаемся к obj.avatar.url без проверки.
        """
        # пробуем вычисляемое/хранимое поле avatar_url
        url = getattr(obj, "avatar_url", None)

        if not url:
            avatar = getattr(obj, "avatar", None)
            # проверяем, что у файла есть имя: это не триггерит ValueError
            if avatar is not None and getattr(avatar, "name", ""):
                try:
                    url = avatar.url
                except Exception:
                    url = None

        request = self.context.get("request")
        if url and request is not None and not str(url).startswith("http"):
            return request.build_absolute_uri(url)
        return url

    def get_rating(self, obj):
        val = getattr(obj, "rating", None)
        try:
            return float(val) if val is not None else 0.0
        except Exception:
            return 0.0
