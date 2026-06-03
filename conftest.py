"""Pytest bootstrap for the mixed Django/Flask test suite.

The project test suite is started with plain ``pytest`` from the repository
root, not with ``manage.py test``.  Therefore Django has to be configured
before pytest imports modules that touch DRF settings or Django models, and a
Django test database has to be prepared for ``django.test.TestCase`` classes.
"""

import os

import pytest


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cinema_project.settings")


def pytest_configure():
    """Initialize Django before test modules are imported during collection."""
    import django
    from django.apps import apps

    if not apps.ready:
        django.setup()


@pytest.fixture(scope="session", autouse=True)
def django_test_environment():
    """Create and tear down the Django test database for plain pytest runs."""
    from django.test.runner import DiscoverRunner
    from django.test.utils import setup_test_environment, teardown_test_environment

    setup_test_environment()
    runner = DiscoverRunner(verbosity=0, interactive=False)
    old_config = runner.setup_databases()

    try:
        yield
    finally:
        runner.teardown_databases(old_config)
        teardown_test_environment()
