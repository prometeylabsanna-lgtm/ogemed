from django.urls import path

from .lead_views import lead_create
from .views import CMSPageDetailView

app_name = "cms"

urlpatterns = [
    path("pro-nas/", CMSPageDetailView.as_view(), {"slug": "pro-nas"}, name="about"),
    path("kontakty/", CMSPageDetailView.as_view(), {"slug": "kontakty"}, name="contacts"),
    path(
        "dostavka-i-oplata/",
        CMSPageDetailView.as_view(),
        {"slug": "dostavka-i-oplata"},
        name="shipping",
    ),
    path(
        "povernennya/",
        CMSPageDetailView.as_view(),
        {"slug": "povernennya"},
        name="returns",
    ),
    path(
        "polityka-konfidentsiynosti/",
        CMSPageDetailView.as_view(),
        {"slug": "polityka-konfidentsiynosti"},
        name="privacy",
    ),
    path(
        "publichna-oferta/",
        CMSPageDetailView.as_view(),
        {"slug": "publichna-oferta"},
        name="offer",
    ),
    path("api/lead/", lead_create, name="lead_create"),
]
