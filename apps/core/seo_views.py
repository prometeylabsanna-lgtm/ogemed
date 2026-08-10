"""robots.txt and sitemap.xml (no django.contrib.sites dependency)."""
from __future__ import annotations

from xml.etree.ElementTree import Element, SubElement, tostring

from django.http import HttpResponse
from django.urls import reverse

from apps.catalog.models import Brand, Category, Product
from apps.cms.models import CMSPage
from apps.core.seo import absolute_url, site_origin


def robots_txt(request):
    origin = site_origin()
    body = "\n".join(
        [
            "User-agent: *",
            "Allow: /",
            "Disallow: /admin/",
            "Disallow: /koshyk/",
            "Disallow: /oformlennya/",
            "Disallow: /dyakuyemo/",
            "Disallow: /kabinet/",
            "Disallow: /vkhid/",
            "Disallow: /reyestratsiya/",
            "Disallow: /payments/",
            "Disallow: /api/",
            "Disallow: /poshuk/",
            f"Sitemap: {origin}/sitemap.xml",
            "",
        ]
    )
    return HttpResponse(body, content_type="text/plain; charset=utf-8")


def _url_el(parent: Element, loc: str, changefreq: str = "weekly", priority: str = "0.5"):
    url = SubElement(parent, "url")
    SubElement(url, "loc").text = loc
    SubElement(url, "changefreq").text = changefreq
    SubElement(url, "priority").text = priority


def sitemap_xml(request):
    urlset = Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")

    _url_el(urlset, absolute_url("/"), changefreq="daily", priority="1.0")
    _url_el(urlset, absolute_url(reverse("catalog:list")), priority="0.9")
    _url_el(urlset, absolute_url(reverse("catalog:brands")), priority="0.7")

    for cat in Category.objects.filter(is_active=True).only("slug"):
        _url_el(urlset, absolute_url(cat.get_absolute_url()), priority="0.8")

    for brand in Brand.objects.filter(is_active=True).only("slug"):
        _url_el(urlset, absolute_url(brand.get_absolute_url()), priority="0.7")

    for product in Product.objects.published().only("slug"):
        _url_el(urlset, absolute_url(product.get_absolute_url()), priority="0.8")

    for page in CMSPage.objects.filter(is_published=True):
        try:
            _url_el(urlset, absolute_url(page.get_absolute_url()), priority="0.6")
        except Exception:
            continue

    raw = tostring(urlset, encoding="utf-8", xml_declaration=True)
    return HttpResponse(raw, content_type="application/xml; charset=utf-8")
