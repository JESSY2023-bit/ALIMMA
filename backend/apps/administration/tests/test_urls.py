from django.urls import resolve


def test_django_admin_is_available():
    assert resolve("/admin/").namespace == "admin"
