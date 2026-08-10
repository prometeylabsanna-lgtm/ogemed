from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordChangeDoneView,
    PasswordChangeView,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext as _
from django.views.generic import FormView

from apps.core.breadcrumbs import build_breadcrumbs
from apps.orders.models import Order, OrderStatus, PaymentType

from .forms import EmailAuthenticationForm, ProfileForm, RegisterForm
from .models import Profile


class UserLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = EmailAuthenticationForm
    redirect_authenticated_user = True

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["page_title"] = _("Вхід")
        ctx["breadcrumbs"] = build_breadcrumbs(self.request, (_("Вхід"), None))
        ctx["next"] = self.request.POST.get("next") or self.request.GET.get("next") or ""
        return ctx


class UserLogoutView(LogoutView):
    next_page = reverse_lazy("core:home")


class RegisterView(FormView):
    template_name = "accounts/register.html"
    form_class = RegisterForm
    success_url = reverse_lazy("accounts:cabinet")

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["page_title"] = _("Реєстрація")
        ctx["breadcrumbs"] = build_breadcrumbs(self.request, (_("Реєстрація"), None))
        return ctx


class AppPasswordResetView(PasswordResetView):
    template_name = "accounts/password_reset.html"
    email_template_name = "accounts/email/password_reset_email.txt"
    subject_template_name = "accounts/email/password_reset_subject.txt"
    success_url = reverse_lazy("accounts:password_reset_done")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["page_title"] = _("Відновлення пароля")
        ctx["breadcrumbs"] = build_breadcrumbs(self.request, (_("Відновлення пароля"), None))
        return ctx


class AppPasswordResetDoneView(PasswordResetDoneView):
    template_name = "accounts/password_reset_done.html"


class AppPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = "accounts/password_reset_confirm.html"
    success_url = reverse_lazy("accounts:password_reset_complete")


class AppPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = "accounts/password_reset_complete.html"


class AppPasswordChangeView(PasswordChangeView):
    template_name = "accounts/password_change.html"
    success_url = reverse_lazy("accounts:password_change_done")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["page_title"] = _("Зміна пароля")
        ctx["breadcrumbs"] = build_breadcrumbs(
            self.request,
            (_("Кабінет"), reverse("accounts:cabinet")),
            (_("Профіль"), reverse("accounts:profile")),
            (_("Зміна пароля"), None),
        )
        return ctx


class AppPasswordChangeDoneView(PasswordChangeDoneView):
    template_name = "accounts/password_change_done.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["page_title"] = _("Пароль змінено")
        ctx["breadcrumbs"] = build_breadcrumbs(
            self.request,
            (_("Кабінет"), reverse("accounts:cabinet")),
            (_("Пароль змінено"), None),
        )
        return ctx


@login_required
def cabinet(request):
    orders = Order.objects.filter(user=request.user)[:5]
    return render(
        request,
        "accounts/cabinet.html",
        {
            "page_title": _("Кабінет"),
            "orders": orders,
            "breadcrumbs": build_breadcrumbs(request, (_("Кабінет"), None)),
        },
    )


@login_required
def profile_view(request):
    profile, _created = Profile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=profile, user=request.user)
        if form.is_valid():
            form.save()
            return redirect("accounts:profile")
    else:
        form = ProfileForm(instance=profile, user=request.user)
    return render(
        request,
        "accounts/profile.html",
        {
            "form": form,
            "page_title": _("Профіль"),
            "breadcrumbs": build_breadcrumbs(
                request,
                (_("Кабінет"), reverse("accounts:cabinet")),
                (_("Профіль"), None),
            ),
        },
    )


@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user)
    return render(
        request,
        "accounts/orders.html",
        {
            "orders": orders,
            "page_title": _("Замовлення"),
            "breadcrumbs": build_breadcrumbs(
                request,
                (_("Кабінет"), reverse("accounts:cabinet")),
                (_("Замовлення"), None),
            ),
        },
    )


@login_required
def order_detail(request, pk):
    order = get_object_or_404(
        Order.objects.prefetch_related("items__product__images"),
        pk=pk,
        user=request.user,
    )
    return render(
        request,
        "accounts/order_detail.html",
        {
            "order": order,
            "page_title": _("Замовлення №%(n)s") % {"n": order.order_number},
            "show_pay": order.status == OrderStatus.AWAITING_PAYMENT
            and order.payment_type == PaymentType.LIQPAY,
            "breadcrumbs": build_breadcrumbs(
                request,
                (_("Кабінет"), reverse("accounts:cabinet")),
                (_("Замовлення"), reverse("accounts:orders")),
                (_("Замовлення №%(n)s") % {"n": order.order_number}, None),
            ),
        },
    )
