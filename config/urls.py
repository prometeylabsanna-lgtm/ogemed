"""URL configuration for OGEMED for you."""
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve as serve_media

from apps.core.seo_views import robots_txt, sitemap_xml
from apps.core.views import health, page_not_found


def _admin_decoy(request):
    """Публічний /admin — завжди 404 (реальна адмінка на settings.ADMIN_URL)."""
    return page_not_found(request, Exception("Not found"))


urlpatterns = [
    path(f"{settings.ADMIN_URL}/", admin.site.urls),
    re_path(r"^admin(?:/.*)?$", _admin_decoy),
    path("healthz/", health, name="healthz"),
    path("robots.txt", robots_txt, name="robots_txt"),
    path("sitemap.xml", sitemap_xml, name="sitemap_xml"),
    path("i18n/", include("django.conf.urls.i18n")),
    path("", include("apps.payments.urls")),
]

urlpatterns += i18n_patterns(
    path("", include("apps.core.urls")),
    path("", include("apps.catalog.urls")),
    path("", include("apps.cart.urls")),
    path("", include("apps.orders.urls")),
    path("", include("apps.shipping.urls")),
    path("", include("apps.accounts.urls")),
    path("", include("apps.cms.urls")),
    prefix_default_language=False,
)

handler404 = "apps.core.views.page_not_found"

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
elif getattr(settings, "SERVE_MEDIA", False):
    urlpatterns += [
        re_path(
            r"^media/(?P<path>.*)$",
            serve_media,
            {"document_root": settings.MEDIA_ROOT},
        ),
    ]
