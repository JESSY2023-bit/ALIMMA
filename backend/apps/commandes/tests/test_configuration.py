from django.conf import settings


def test_default_page_size_is_twenty():
    assert settings.REST_FRAMEWORK["PAGE_SIZE"] == 20
