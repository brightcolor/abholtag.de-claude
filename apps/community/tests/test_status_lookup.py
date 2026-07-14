import pytest
from django.urls import reverse

from apps.community.models import ErrorReport, ReportCategory


@pytest.fixture
def report(db):
    return ErrorReport.objects.create(
        category=ReportCategory.WRONG_HOUSE_RANGE,
        description="Hausnummern 1-23 sind falsch zugeordnet.",
    )


def test_lookup_page_renders(client):
    resp = client.get(reverse("report_status_lookup"))
    assert resp.status_code == 200
    assert b"Vorgangsnummer" in resp.content


def test_lookup_redirects_to_existing_report(client, report):
    resp = client.post(reverse("report_status_lookup"), {"nummer": report.public_token})
    assert resp.status_code == 302
    assert resp.url == reverse("report_status", kwargs={"token": report.public_token})


def test_lookup_is_case_insensitive(client, report):
    resp = client.post(reverse("report_status_lookup"), {"nummer": report.public_token.lower()})
    assert resp.status_code == 302
    assert resp.url == reverse("report_status", kwargs={"token": report.public_token})


def test_lookup_unknown_number_shows_error(client, db):
    resp = client.post(reverse("report_status_lookup"), {"nummer": "DOESNOTEX99"})
    assert resp.status_code == 200
    assert "keine Meldung gefunden".encode() in resp.content


def test_report_form_links_to_lookup(client, db):
    resp = client.get(reverse("report_form"))
    assert resp.status_code == 200
    assert reverse("report_status_lookup").encode() in resp.content


def test_status_page_renders_lookup_link(client, report):
    resp = client.get(reverse("report_status", kwargs={"token": report.public_token}))
    assert resp.status_code == 200
    assert reverse("report_status_lookup").encode() in resp.content
