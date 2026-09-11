"""Перегнати існуючі JPG/PNG у WebP + _thumb.webp (той самий пайплайн, що upload)."""

from __future__ import annotations

from django.apps import apps
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from apps.core.fields import OptimizedImageField
from apps.core.image_processing import (
    process_upload,
    thumb_storage_name,
)


class Command(BaseCommand):
    help = "Конвертує вже збережені растрові зображення в WebP і генерує мініатюри."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Лише показати, що буде змінено.",
        )

    def handle(self, *args, **options):
        dry = options["dry_run"]
        converted = 0
        skipped = 0
        errors = 0

        for model in apps.get_models():
            fields = [
                field
                for field in model._meta.local_fields
                if isinstance(field, OptimizedImageField)
            ]
            if not fields:
                continue
            for instance in model._default_manager.all().iterator():
                for field in fields:
                    result = self._reprocess_field(instance, field, dry)
                    if result == "converted":
                        converted += 1
                    elif result == "skipped":
                        skipped += 1
                    elif result == "error":
                        errors += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"reprocess_images: converted={converted} skipped={skipped} errors={errors}"
            )
        )

    def _reprocess_field(self, instance, field: OptimizedImageField, dry: bool) -> str:
        file = getattr(instance, field.attname)
        name = getattr(file, "name", "") or ""
        if not name:
            return "skipped"
        lower = name.lower()
        if lower.endswith(".svg"):
            return "skipped"
        storage = file.storage
        has_thumb = False
        try:
            has_thumb = storage.exists(thumb_storage_name(name))
        except Exception:
            has_thumb = False
        if lower.endswith(".webp") and has_thumb:
            return "skipped"

        label = f"{instance._meta.label}.{field.name} id={instance.pk} {name}"
        if dry:
            self.stdout.write(f"  would convert {label}")
            return "converted"

        try:
            if not storage.exists(name):
                self.stderr.write(f"  missing file {label}")
                return "error"
            with storage.open(name, "rb") as src:
                raw = src.read()
            upload = ContentFile(raw, name=name)
            main, thumb = process_upload(
                upload,
                max_side=field.max_side,
                quality=field.quality,
                generate_thumb=field.generate_thumb,
                allow_svg=field.allow_svg,
                original_name=name,
            )
            old_name = name
            file.save(main.name, main, save=False)
            setattr(instance, field.attname, file)
            instance.save(update_fields=[field.name])
            if thumb is not None:
                thumb_name = thumb_storage_name(file.name)
                if not storage.exists(thumb_name):
                    storage.save(thumb_name, thumb)
            if old_name and old_name != file.name:
                try:
                    storage.delete(old_name)
                except Exception:
                    pass
                old_thumb = thumb_storage_name(old_name)
                if old_thumb and old_thumb != old_name:
                    try:
                        storage.delete(old_thumb)
                    except Exception:
                        pass
            self.stdout.write(f"  converted {label} -> {file.name}")
            return "converted"
        except Exception as exc:
            self.stderr.write(f"  failed {label}: {exc}")
            return "error"
