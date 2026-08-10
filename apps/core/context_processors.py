from apps.catalog.services import nav_categories, top_level_categories
from apps.core.breadcrumbs import language_switch_urls
from apps.core.models import SiteSettings
from apps.core.seo import canonical_for_request, hreflang_map


def site_settings(request):
    """Inject singleton SiteSettings, language switch URLs, footer categories."""
    try:
        settings_obj = SiteSettings.load()
    except Exception:
        settings_obj = None
    try:
        footer_categories = [
            cat
            for cat in top_level_categories()[:8]
            if (cat.slug or "").lower() != "qa"
            and (getattr(cat, "name_uk", "") or "").strip().lower() != "qa"
            and (getattr(cat, "name_ru", "") or "").strip().lower() != "qa"
        ][:6]
    except Exception:
        footer_categories = []
    try:
        catalog_nav = list(nav_categories())
    except Exception:
        catalog_nav = []
    return {
        "site_settings": settings_obj,
        "lang_urls": language_switch_urls(request),
        "footer_categories": footer_categories,
        "catalog_nav": catalog_nav,
        "canonical_url": canonical_for_request(request),
        "hreflang_urls": hreflang_map(request),
        "robots_noindex": False,
    }
