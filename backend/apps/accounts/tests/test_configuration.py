from django.conf import settings


def test_jwt_is_default_authentication():
    assert settings.REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"] == (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    )
