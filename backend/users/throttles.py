# users/throttles.py
from rest_framework.throttling import SimpleRateThrottle

class LoginRateThrottle(SimpleRateThrottle):
    """
    Ограничение частоты попыток логина.
    Ключ строится из IP-адреса и идентификатора аккаунта (email/username),
    чтобы не дать одному IP бесконечно брутфорсить один и тот же аккаунт.
    Использует REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['login'].
    """
    scope = "login"

    def get_cache_key(self, request, view):
        ident = self.get_ident(request)  # IP клиента
        user_key = (request.data.get("email") or request.data.get("username") or "").strip().lower()
        if not user_key:
            user_key = "anonymous"
        return f"throttle_login:{ident}:{user_key}"
