"""Middleware: адмінка UA, CSP, media cache."""
from __future__ import annotations

from django.conf import settings
from django.utils import translation


class ForceAdminUkrainianMiddleware:
    """Адмінка завжди українською, незалежно від cookie / Accept-Language."""

    def __init__(self, get_response):
        self.get_response = get_response
        self._prefix = f"/{(getattr(settings, 'ADMIN_URL', 'admin') or 'admin').strip('/')}/"

    def __call__(self, request):
        if not request.path.startswith(self._prefix):
            return self.get_response(request)

        # override тримає uk на весь request (activate інколи скидає LocaleMiddleware / view).
        with translation.override("uk"):
            request.LANGUAGE_CODE = "uk"
            response = self.get_response(request)
        response.headers.setdefault("Content-Language", "uk")
        return response


class ContentSecurityPolicyMiddleware:
    """Enforce a baseline CSP without Trusted Types (HTMX-safe)."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if "Content-Security-Policy" in response:
            return response
        admin_prefix = f"/{(getattr(settings, 'ADMIN_URL', 'admin') or 'admin').strip('/')}/"
        if request.path.startswith(admin_prefix):
            return response
        img_src = "'self' data: blob:"
        s3_domain = (getattr(settings, "AWS_S3_CUSTOM_DOMAIN", "") or "").strip()
        if s3_domain:
            img_src = f"{img_src} https://{s3_domain}"
        endpoint = (getattr(settings, "AWS_S3_ENDPOINT_URL", "") or "").strip()
        if endpoint.startswith("http"):
            img_src = f"{img_src} {endpoint}"
        csp = (
            "default-src 'self'; "
            "base-uri 'self'; "
            "object-src 'none'; "
            "frame-ancestors 'none'; "
            "form-action 'self'; "
            f"img-src {img_src}; "
            "font-src 'self'; "
            "style-src 'self' 'unsafe-inline'; "
            "script-src 'self'; "
            "connect-src 'self'; "
            "upgrade-insecure-requests"
        )
        response["Content-Security-Policy"] = csp
        return response


class MediaCacheControlMiddleware:
    """Довгий Cache-Control для /media/ коли Django сам віддає файли."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        path = request.path or ""
        if path.startswith("/media/") and response.status_code == 200:
            if "Cache-Control" not in response:
                response["Cache-Control"] = "public, max-age=86400"
        return response
