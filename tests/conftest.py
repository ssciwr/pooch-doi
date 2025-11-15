import pytest
import requests_mock
from unittest.mock import MagicMock, patch
from contextlib import contextmanager


# This class can be used to specifically make a set of mock data repositories available.
# It can be used as a function call or a context manager.
class _MakeReposAvailable:
    def __init__(self):
        self.entries = []
        self.patcher = patch("importlib.metadata.entry_points")

    def __call__(self, *repos):
        self.entries = [MagicMock() for _ in repos]
        for e,r in zip(self.entries,repos):
            e.load.return_value = r
        self._patch()
        return self

    def __enter__(self):
        pass

    def __exit__(self, type, value, traceback):
        self._unpatch()
        return False

    def _patch(self):
        mock = self.patcher.start()
        mock.return_value = self.entries

    def _unpatch(self):
        self.patcher.stop()

_REPO_PATCHER = _MakeReposAvailable()

@pytest.fixture
def make_repos_available():
    return _REPO_PATCHER


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
