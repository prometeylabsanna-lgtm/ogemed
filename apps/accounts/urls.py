from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("vkhid/", views.UserLoginView.as_view(), name="login"),
    path("vyhid/", views.UserLogoutView.as_view(), name="logout"),
    path("reyestratsiya/", views.RegisterView.as_view(), name="register"),
    path("kabinet/", views.cabinet, name="cabinet"),
    path("kabinet/profil/", views.profile_view, name="profile"),
    path("kabinet/parol/", views.AppPasswordChangeView.as_view(), name="password_change"),
    path(
        "kabinet/parol/gotovo/",
        views.AppPasswordChangeDoneView.as_view(),
        name="password_change_done",
    ),
    path("kabinet/zamovlennya/", views.order_list, name="orders"),
    path("kabinet/zamovlennya/<int:pk>/", views.order_detail, name="order_detail"),
    path(
        "vidnovlennya-parolya/",
        views.AppPasswordResetView.as_view(),
        name="password_reset",
    ),
    path(
        "vidnovlennya-parolya/nadislano/",
        views.AppPasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "vidnovlennya-parolya/<uidb64>/<token>/",
        views.AppPasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "vidnovlennya-parolya/gotovo/",
        views.AppPasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
]
