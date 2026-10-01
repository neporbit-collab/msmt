from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls
from wagtail import urls as wagtail_urls
from core.views import inquiry, public_media

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("inquiry/", inquiry, name="inquiry"),
    path("media/<path:path>", public_media, name="public_media"),
    path("admin/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    path("", include(wagtail_urls)),
]
