from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/accounts/", include("users.urls")),  # ваши аккаунты
    path("api/jobs/", include("jobs.urls")),       # ✅ эндпоинты визарда задач
]

# Медиа-файлы в режиме разработки
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
