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


# ---------------------------
# Регистрация
# ---------------------------
class RegisterSerializer(serializers.ModelSerializer):
    confirm = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=User.ROLE_CHOICES)
    phone = serializers.CharField(validators=[phone_validator])

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
            "phone",
            "role",
            "password",
            "confirm",
        )
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


# ---------------------------
# Профиль (read-only для фронта)
# ---------------------------
class ProfileSerializer(serializers.ModelSerializer):
    avatar_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            "id", "email", "phone", "role",
            "first_name", "last_name", "username",
            "avatar_url",
        )
        read_only_fields = fields

    def get_avatar_url(self, obj):
        url = getattr(obj, "avatar_url", None)
        request = self.context.get("request")
        if url and request is not None and not str(url).startswith("http"):
            return request.build_absolute_uri(url)
        return url


# ---------------------------
# Загрузка аватара (multipart/form-data)
# ---------------------------
class AvatarUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("avatar",)

    def update(self, instance, validated_data):
        # Здесь можно удалить старый файл, если нужно.
        return super().update(instance, validated_data)


# ---------------------------
# Обновление публичной анкеты (JSON, PATCH)
# ВАЖНО: пока это Serializer, чтобы не падать, если часть полей ещё не создана в модели.
# После добавления полей в модель — будет сохранять 1-в-1.
# ---------------------------
class PublicProfileUpdateSerializer(serializers.Serializer):
    # базовые поля анкеты
    title = serializers.CharField(required=False, allow_blank=True, default="")
    bio = serializers.CharField(required=False, allow_blank=True, default="")
    location = serializers.CharField(required=False, allow_blank=True, default="")
    gender = serializers.CharField(required=False, allow_blank=True, default="")
    education = serializers.CharField(required=False, allow_blank=True, default="")
    status = serializers.ChoiceField(
        choices=[("open", "open"), ("partial", "partial"), ("busy", "busy")],
        required=False,
        default="open",
    )

    # списки
    categories = serializers.ListField(
        child=serializers.CharField(), required=False, default=list
    )
    skills = serializers.ListField(
        child=serializers.CharField(), required=False, default=list
    )

    # ставки
    rate_type = serializers.ChoiceField(
        choices=[("hour", "hour"), ("project", "project")],
        required=False,
        default="hour",
    )
    hourly_rate = serializers.IntegerField(required=False, allow_null=True)
    project_rate = serializers.IntegerField(required=False, allow_null=True)
    availability = serializers.BooleanField(required=False, default=True)

    # ссылки/соцсети/портфолио
    links = serializers.ListField(
        child=serializers.DictField(child=serializers.CharField(allow_blank=True)),
        required=False,
        default=list,
    )
    socials = serializers.DictField(
        child=serializers.CharField(allow_blank=True),
        required=False,
        default=dict,
    )
    portfolio = serializers.ListField(
        child=serializers.DictField(child=serializers.CharField(allow_blank=True)),
        required=False,
        default=list,
    )

    # календарь занятости (строки 'YYYY-MM-DD')
    busy_dates = serializers.ListField(
        child=serializers.RegexField(r"^\d{4}-\d{2}-\d{2}$"),
        required=False,
        default=list,
    )

    def validate(self, attrs):
        rate_type = attrs.get("rate_type", "hour")
        hourly = attrs.get("hourly_rate")
        project = attrs.get("project_rate")

        if rate_type == "hour":
            # hourly_rate должен быть > 0, project_rate игнорируем
            if hourly is None or hourly <= 0:
                raise serializers.ValidationError({"hourly_rate": "Укажи корректную почасовую ставку"})
            attrs["project_rate"] = None
        else:
            # project_rate должен быть > 0, hourly_rate игнорируем
            if project is None or project <= 0:
                raise serializers.ValidationError({"project_rate": "Укажи корректную ставку за проект"})
            attrs["hourly_rate"] = None

        return attrs

    def update(self, instance, validated_data):
        """
        Аккуратно записываем только те поля, которые реально существуют в модели.
        Это позволит сейчас не падать, а после расширения модели — начать сохранять без правок фронта.
        """
        changed = False
        for field, value in validated_data.items():
            if hasattr(instance, field):
                setattr(instance, field, value)
                changed = True
        if changed:
            instance.save(update_fields=[
                f for f in validated_data.keys() if hasattr(instance, f)
            ])
        return instance

    def create(self, validated_data):
        raise NotImplementedError("Используйте update() для изменения профиля пользователя.")


# ---------------------------
# Логин по email/username (JWT)
# ---------------------------
class EmailTokenObtainPairSerializer(serializers.Serializer):
    """
    Принимает либо email, либо username + password.
    Возвращает пару токенов {access, refresh}.
    """
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
        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }
