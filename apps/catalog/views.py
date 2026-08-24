from django.core.paginator import Paginator
from django.db.models import Prefetch, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views.decorators.http import require_GET
from django.views.generic import DetailView, ListView, TemplateView

from apps.core.breadcrumbs import build_breadcrumbs
from apps.core.seo import seo_from_object

from .labels import label_by_slug
from .models import AttributeValue, Brand, Category, Product
from .services import (
    CATALOG_SORT_OPTIONS,
    CATALOG_VIEW_OPTIONS,
    SKIN_TYPE_SELECT,
    apply_catalog_filters,
    apply_catalog_sort,
    catalog_controls_context,
    catalog_query_string,
    category_branch_ids,
    get_active_variant,
    has_active_filters,
    is_skin_type_select,
    published_products,
    resolve_catalog_view,
    search_products,
    variant_gallery,
)
from .variant_matrix import build_variant_option_groups, uses_flat_variant_labels

PER_PAGE = 12
SUGGEST_LIMIT = 8
SUGGEST_MIN_LEN = 2


class CatalogListView(ListView):
    template_name = "catalog/list.html"
    context_object_name = "products"
    paginate_by = PER_PAGE

    def get_queryset(self):
        qs = published_products()
        qs = apply_catalog_filters(qs, self.request.GET)
        return apply_catalog_sort(qs, self.request.GET.get("sort"))

    def get_template_names(self):
        if self.request.htmx:
            if self.request.GET.get("more"):
                return ["catalog/partials/_product_cards_more.html"]
            return ["catalog/partials/_product_grid.html"]
        return [self.template_name]

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(catalog_controls_context())
        ctx["page_title"] = _("Каталог")
        ctx["current_sort"] = self.request.GET.get("sort", "novelty")
        ctx["current_view"] = resolve_catalog_view(self.request.GET)
        ctx["selected_attrs"] = self.request.GET.getlist("attr")
        ctx["selected_brand"] = self.request.GET.get("brand", "")
        ctx["selected_availability"] = self.request.GET.get("availability", "")
        ctx["selected_label"] = label_by_slug(self.request.GET.get("label"))
        if ctx["selected_label"] is not None:
            label = ctx["selected_label"]
            ctx["selected_label_title"] = label.display_title()
        skin_type = (self.request.GET.get("skin_type") or "").strip()
        ctx["selected_skin_type"] = (
            "" if skin_type == SKIN_TYPE_SELECT else skin_type
        )
        ctx["skin_type_select"] = is_skin_type_select(self.request.GET)
        ctx["filter_query"] = catalog_query_string(self.request.GET)
        ctx["has_active_filters"] = has_active_filters(self.request.GET)
        ctx["breadcrumbs"] = build_breadcrumbs(self.request, (_("Каталог"), None))
        ctx["list_url"] = self.request.path
        return ctx


class CategoryDetailView(CatalogListView):
    template_name = "catalog/category.html"

    def dispatch(self, request, *args, **kwargs):
        self.category = get_object_or_404(
            Category.objects.filter(is_active=True),
            slug=kwargs["slug"],
        )
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        branch = category_branch_ids(self.category)
        qs = (
            published_products()
            .filter(Q(primary_category_id__in=branch) | Q(categories__id__in=branch))
            .distinct()
        )
        qs = apply_catalog_filters(qs, self.request.GET)
        return apply_catalog_sort(qs, self.request.GET.get("sort"))

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        cat = self.category
        crumbs = []
        for ancestor in cat.get_ancestors():
            crumbs.append((ancestor.name, ancestor.get_absolute_url()))
        crumbs.append((cat.name, None))
        ctx.update(
            seo_from_object(
                cat,
                fallback_title=cat.name,
                fallback_description=cat.name,
            )
        )
        ctx["category"] = cat
        ctx["breadcrumbs"] = build_breadcrumbs(
            self.request,
            (_("Каталог"), "/katalog/"),
            *crumbs,
        )
        return ctx


class BrandListView(ListView):
    template_name = "catalog/brands.html"
    context_object_name = "brands"

    def get_queryset(self):
        return Brand.objects.filter(is_active=True)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["page_title"] = _("Бренди")
        ctx["nav_section"] = "brands"
        ctx["breadcrumbs"] = build_breadcrumbs(self.request, (_("Бренди"), None))
        return ctx


class BrandDetailView(ListView):
    template_name = "catalog/brand_detail.html"
    context_object_name = "products"
    paginate_by = PER_PAGE

    def dispatch(self, request, *args, **kwargs):
        self.brand = get_object_or_404(
            Brand.objects.filter(is_active=True),
            slug=kwargs["slug"],
        )
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        qs = published_products().filter(brand=self.brand)
        return apply_catalog_sort(qs, self.request.GET.get("sort"))

    def get_template_names(self):
        if self.request.htmx:
            if self.request.GET.get("more"):
                return ["catalog/partials/_product_cards_more.html"]
            return ["catalog/partials/_product_grid.html"]
        return [self.template_name]

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(
            seo_from_object(
                self.brand,
                fallback_title=self.brand.name,
                fallback_description=self.brand.tagline or self.brand.name,
            )
        )
        ctx["brand"] = self.brand
        ctx["nav_section"] = "brands"
        ctx["current_sort"] = self.request.GET.get("sort", "novelty")
        ctx["current_view"] = resolve_catalog_view(self.request.GET)
        ctx["sort_options"] = CATALOG_SORT_OPTIONS
        ctx["view_options"] = CATALOG_VIEW_OPTIONS
        ctx["filter_query"] = catalog_query_string(self.request.GET)
        ctx["list_url"] = self.request.path
        ctx["empty_text"] = _("Товарів цього бренду поки немає")
        ctx["breadcrumbs"] = build_breadcrumbs(
            self.request,
            (_("Бренди"), reverse("catalog:brands")),
            (self.brand.name, None),
        )
        return ctx


class ProductDetailView(DetailView):
    model = Product
    template_name = "catalog/product_detail.html"
    context_object_name = "product"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        attrs_qs = AttributeValue.objects.select_related("attribute").order_by(
            "attribute__sort_order", "sort_order", "pk"
        )
        return (
            Product.objects.published()
            .select_related("brand", "primary_category")
            .prefetch_related(
                "images",
                "variants__attribute_values__attribute",
                Prefetch("attribute_values", queryset=attrs_qs),
                "categories",
            )
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        product = self.object
        variant = get_active_variant(product, self.request.GET.get("variant"))
        variants = [
            v for v in product.variants.all() if v.is_active
        ]
        variants.sort(key=lambda v: (v.sort_order, v.pk))
        option_groups = build_variant_option_groups(variants, variant)
        ctx["variant"] = variant
        ctx["variants"] = variants
        ctx["variant_option_groups"] = option_groups
        ctx["variant_flat_labels"] = uses_flat_variant_labels(variants, option_groups)
        ctx["gallery"] = variant_gallery(product, variant)
        ctx.update(
            seo_from_object(
                product,
                fallback_title=product.name,
                fallback_description=product.short_description or product.name,
            )
        )
        crumbs = [(_("Каталог"), "/katalog/")]
        if product.primary_category_id:
            cat = product.primary_category
            for ancestor in cat.get_ancestors():
                crumbs.append((ancestor.name, ancestor.get_absolute_url()))
            crumbs.append((cat.name, cat.get_absolute_url()))
        crumbs.append((product.name, None))
        ctx["breadcrumbs"] = build_breadcrumbs(self.request, *crumbs)
        return ctx

    def get_template_names(self):
        if self.request.htmx and self.request.GET.get("partial") == "variant":
            return ["catalog/partials/_variant_block.html"]
        return [self.template_name]


class SearchView(TemplateView):
    template_name = "catalog/search.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        q = (self.request.GET.get("q") or "").strip()
        products = search_products(q) if q else Product.objects.none()
        paginator = Paginator(products, PER_PAGE)
        page = paginator.get_page(self.request.GET.get("page") or 1)
        ctx["q"] = q
        ctx["products"] = page.object_list
        ctx["page_obj"] = page
        ctx["filter_query"] = catalog_query_string(self.request.GET)
        ctx["list_url"] = self.request.path
        ctx["current_view"] = resolve_catalog_view(self.request.GET)
        ctx["page_title"] = _("Пошук")
        ctx["robots_noindex"] = True
        ctx["breadcrumbs"] = build_breadcrumbs(self.request, (_("Пошук"), None))
        return ctx

    def get_template_names(self):
        if self.request.htmx:
            if self.request.GET.get("more"):
                return ["catalog/partials/_product_cards_more.html"]
            return ["catalog/partials/_product_grid.html"]
        return [self.template_name]


@require_GET
def search_suggest(request):
    """JSON підказки для live-search у шапці."""
    q = (request.GET.get("q") or "").strip()
    if len(q) < SUGGEST_MIN_LEN:
        return JsonResponse({"q": q, "results": []})

    products = (
        search_products(q)
        .select_related("brand")
        .prefetch_related("images", "variants")[:SUGGEST_LIMIT]
    )
    results = []
    for product in products:
        image = product.main_image()
        variant = product.default_variant()
        results.append(
            {
                "name": product.name,
                "url": product.get_absolute_url(),
                "brand": product.brand.name if product.brand_id else "",
                "price": str(variant.price) if variant else "",
                "sku": variant.sku if variant else "",
                "image": image.image.url if image and image.image else "",
            }
        )
    return JsonResponse({"q": q, "results": results})
