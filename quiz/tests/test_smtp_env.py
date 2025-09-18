import os


def test_smtp_env_not_placeholder():
    """If EMAIL_BACKEND is set to SMTP via environment, ensure EMAIL_HOST_USER and
    EMAIL_HOST_PASSWORD are not the default placeholders. This avoids importing
    Django settings when running pytest directly.
    """
    backend = os.getenv("EMAIL_BACKEND", "")
    if "smtp" in backend.lower():
        user = os.getenv("EMAIL_HOST_USER", "")
        pwd = os.getenv("EMAIL_HOST_PASSWORD", "")
        assert user and user != "you@example.com", "EMAIL_HOST_USER looks like the placeholder"
        assert pwd and pwd != "CHANGE_ME", "EMAIL_HOST_PASSWORD looks like the placeholder"
    else:
        # Not using SMTP backend in this environment — test is not applicable
        assert True
