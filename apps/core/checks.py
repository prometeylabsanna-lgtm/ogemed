"""Django system checks for integration env (warnings, never hard-fail local)."""
from __future__ import annotations

from django.conf import settings
from django.core.checks import Warning, register

from .integrations import all_integration_statuses


@register(deploy=True)
def check_integrations(app_configs, **kwargs):
    warnings = []
    for status in all_integration_statuses():
        if status.configured:
            continue
        warnings.append(
            Warning(
                f"Integration «{status.key}» not fully configured: {status.detail}",
                id=f"core.W{status.key[:8].upper()}",
            )
        )

    if not (settings.FROM_EMAIL or "").strip():
        warnings.append(
            Warning(
                "FROM_EMAIL is empty — transactional email uses noreply@example.com fallback.",
                id="core.WFROMMAIL",
            )
        )
    return warnings
