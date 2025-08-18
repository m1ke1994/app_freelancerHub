from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from rest_framework import serializers

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
        # Уникальность заранее, чтобы не ловить IntegrityError
        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError("Пользователь с таким e-mail уже существует")
        return email

    def validate_phone(self, value: str) -> str:
        phone = (value or "").strip()
        # phone_validator уже проверит формат; здесь проверим уникальность
        if User.objects.filter(phone=phone).exists():
            raise serializers.ValidationError("Пользователь с таким телефоном уже существует")
        return phone

    def validate(self, attrs):
        if attrs.get("password") != attrs.get("confirm"):
            raise serializers.ValidationError({"confirm": "Пароли не совпадают"})
        return attrs

    def create(self, validated_data):
        # username = email
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
    class Meta:
        model = User
        fields = ("id", "email", "phone", "role", "first_name", "last_name", "username")
        read_only_fields = fields
