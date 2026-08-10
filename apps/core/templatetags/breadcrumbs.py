from django import template

from apps.core.breadcrumbs import BreadcrumbItem

register = template.Library()


@register.inclusion_tag("partials/breadcrumbs.html", takes_context=True)
def render_breadcrumbs(context, breadcrumbs=None):
    """Render breadcrumbs from context or explicit list."""
    items = breadcrumbs if breadcrumbs is not None else context.get("breadcrumbs")
    if not items:
        return {"breadcrumbs": []}
    normalized: list[BreadcrumbItem] = []
    for item in items:
        if isinstance(item, BreadcrumbItem):
            normalized.append(item)
        elif isinstance(item, dict):
            normalized.append(
                BreadcrumbItem(label=item.get("label", ""), url=item.get("url"))
            )
        else:
            label, url = item
            normalized.append(BreadcrumbItem(label=label, url=url))
    return {"breadcrumbs": normalized}
