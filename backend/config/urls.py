# project/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Django admin
    path("admin/", admin.site.urls),

    # Пользователи: регистрация, логин, профиль
    path("api/accounts/", include("users.urls")),

    # Задания/каталог
    path("api/jobs/", include("jobs.urls")),    # основной путь
    path("api/tasks/", include("jobs.urls")),   # алиас для совместимости фронта
]

# Раздача медиафайлов в режиме DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
