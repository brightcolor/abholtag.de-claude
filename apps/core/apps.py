from django.apps import AppConfig
from django.conf import settings


class CoreConfig(AppConfig):
    name = "apps.core"
    verbose_name = "Basis"

    def ready(self):
        # Two-factor auth for the admin (§34): opt-in, not a hard lockout.
        # Enabling ADMIN_OTP_REQUIRED makes 2FA *available and enforced for
        # accounts that set up a device*, while admins without one still log in
        # with password only (SoftOTPAdminSite). This avoids locking everyone out
        # the moment 2FA is switched on.
        if settings.ADMIN_OTP_REQUIRED:
            from django.contrib import admin

            from apps.core.admin_site import SoftOTPAdminSite

            admin.site.__class__ = SoftOTPAdminSite
