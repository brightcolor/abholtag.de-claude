from django.contrib.admin import AdminSite
from django_otp import user_has_device
from django_otp.admin import OTPAdminSite


class SoftOTPAdminSite(OTPAdminSite):
    """Opt-in two-factor auth for /admin instead of a hard lockout.

    The stock ``OTPAdminSite`` refuses access to *every* admin user until they
    have set up and verified a TOTP device – which locks out admins that never
    configured 2FA (and is a chicken-and-egg problem: you need to log in to add
    a device). This variant keeps 2FA available and enforces it *only for users
    who have actually set up a confirmed device*; everyone else logs in with
    just username + password and can add a second factor later.
    """

    def has_permission(self, request):
        # Base Django staff/active check (bypasses OTPAdminSite's hard is_verified
        # requirement so we can apply our own, softer rule).
        if not AdminSite.has_permission(self, request):
            return False

        # Users who opted into 2FA must still pass it; users without a device may
        # proceed with password-only.
        if user_has_device(request.user, confirmed=True):
            return request.user.is_verified()

        return True
