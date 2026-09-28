from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from apps.core.middleware import ContentSecurityPolicyMiddleware


class ContentSecurityPolicyTests(TestCase):
    def test_form_action_allows_monobank_pay_hosts(self):
        middleware = ContentSecurityPolicyMiddleware(lambda _request: HttpResponse("ok"))
        response = middleware(RequestFactory().get("/"))
        csp = response["Content-Security-Policy"]
        self.assertIn("form-action 'self'", csp)
        self.assertIn("https://pay.monobank.ua", csp)
        self.assertIn("https://pay.mbnk.biz", csp)
