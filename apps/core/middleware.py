"""Примусова українська мова в адмінці (UI Django/Unfold)."""
from __future__ import annotations

from django.conf import settings
from django.utils import translation


class ForceAdminUkrainianMiddleware:
    """Адмінка завжди українською, незалежно від cookie / Accept-Language."""

    def __init__(self, get_response):
        self.get_response = get_response
        self._prefix = f"/{(getattr(settings, 'ADMIN_URL', 'admin') or 'admin').strip('/')}/"

    def __call__(self, request):
        if request.path.startswith(self._prefix):
            translation.activate("uk")
            request.LANGUAGE_CODE = "uk"
        response = self.get_response(request)
        if request.path.startswith(self._prefix):
            response.headers.setdefault("Content-Language", "uk")
        return response
