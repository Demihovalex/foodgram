from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    # Ваши кастомные маршруты
    path("api/", include("api.urls")),
    # Djoser на /api/ (нужно для фронтенда)
    path("api/", include("djoser.urls")),
    path("api/", include("djoser.urls.authtoken")),
    # Djoser на /api/auth/ (нужно для Postman коллекции)
    path("api/auth/", include("djoser.urls")),
    path("api/auth/", include("djoser.urls.authtoken")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
