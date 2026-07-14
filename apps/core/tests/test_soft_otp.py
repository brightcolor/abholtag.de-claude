import pytest
from django_otp.plugins.otp_totp.models import TOTPDevice

from apps.accounts.models import User
from apps.core.admin_site import SoftOTPAdminSite


@pytest.fixture
def staff(db):
    return User.objects.create_user(
        username="staffy", password="pw", is_staff=True, is_active=True
    )


def test_user_without_device_may_log_in(rf, staff):
    """Opt-in 2FA: no configured device -> password-only access is allowed."""
    request = rf.get("/admin/")
    request.user = staff

    assert SoftOTPAdminSite().has_permission(request) is True


def test_user_with_device_must_verify(rf, staff):
    """A user who set up a confirmed device must still pass the second factor."""
    TOTPDevice.objects.create(user=staff, name="phone", confirmed=True)
    request = rf.get("/admin/")
    request.user = staff
    # OTPMiddleware would normally attach is_verified(); simulate "not verified".
    staff.is_verified = lambda: False

    assert SoftOTPAdminSite().has_permission(request) is False


def test_non_staff_is_rejected(rf, db):
    user = User.objects.create_user(username="plain", password="pw", is_active=True)
    request = rf.get("/admin/")
    request.user = user

    assert SoftOTPAdminSite().has_permission(request) is False
