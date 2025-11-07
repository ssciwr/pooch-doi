import pytest
import requests_mock
from contextlib import contextmanager


@pytest.fixture
def doi_mock():
    @contextmanager
    def _mock(doi: str, archive_url: str, status_code: int=200):
        # patch request to doi.org and the resolved URL,
        # because doi_to_url does follow redirects.
        m = requests_mock.Mocker()
        m.start()
        m.get(f"https://doi.org/{doi}", status_code=302, headers={"Location": archive_url})
        m.get(archive_url, status_code=status_code)
        try:
            yield
        finally:
            m.stop()
    return _mock


def pytest_configure(config):
    config.addinivalue_line("markers", "slow: marks tests as slow")
    config.addinivalue_line("markers", "unit: marks tests as unit tests")
    config.addinivalue_line("markers", "integration: marks tests as integration test")
