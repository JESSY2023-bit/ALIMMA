from django.conf import settings


def test_exception_handler_is_configured():
    assert settings.REST_FRAMEWORK["EXCEPTION_HANDLER"] == "config.exceptions.api_exception_handler"
