"""Set DJANGO_SETTINGS_MODULE before Django loads (Vercel build may leave it empty)."""
import os


def configure_settings_module() -> None:
    if os.environ.get("VERCEL"):
        os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings.production"
        return
    if not (os.environ.get("DJANGO_SETTINGS_MODULE") or "").strip():
        os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings.local"
