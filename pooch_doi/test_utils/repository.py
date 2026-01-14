try:
    import pytest
except ImportError:
    raise ImportError(
        """
    Pytest is not installed. To use the provided pooch-doi testing utilities,
    please install pytest.
    """
    )

from typing import Optional, Union, Tuple
import random
import string
import os
from unittest.mock import MagicMock
from urllib.parse import urljoin
from pooch_doi.repository import DataRepository

# ==============================================================
# Internal random helpers:


def _random_string(
    alphabet: Optional[str] = None, length: Optional[Union[int, Tuple[int, int]]] = 10
) -> str:
    alphabet: str = (
        alphabet if alphabet is not None else string.ascii_letters + string.digits
    )
    length = length if isinstance(length, int) else random.randint(length[0], length[1])
    return "".join(random.choices(alphabet, k=length))


def _random_base_url() -> str:
    return f"https://{_random_string()}.{_random_string(length=(2, 4))}"


def _random_archive_path() -> str:
    archive_path = ""
    for _ in range(random.randint(1, 6)):
        archive_path += "/" + _random_string(length=(5, 15))
    return archive_path


def _random_archive_url() -> str:
    return _random_base_url() + _random_archive_path()


def _random_doi() -> str:
    return _random_string(length=(5, 10))


def _value_or(value, alternative):
    return value if value is not None else alternative


# ==============================================================


def _is_online_testing_enabled():
    try:
        return bool(int(os.getenv("POOCH_DOI_ONLINE", default=0)))
    except ValueError:
        return False


try:
    import requests_mock

    class EndpointMocker(requests_mock.Mocker):
        def __init__(self, *args, **kwargs):
            self.base_url = kwargs.pop("base_url", "")
            super().__init__(*args, **kwargs)

        def register_uri(self, *args, **kwargs):
            args = list(args)
            if len(args) >= 2:
                method, uri, *rest = args
                args = (method, urljoin(self.base_url, uri), *rest)
            super().register_uri(*tuple(args), **kwargs)

except ImportError:
    raise ImportError(
        "requests_mock is not installed. To use the mocking capabilities, please install requests_mock"
    )


def _new_endpoint_mocker(base_url: Optional[str] = None, always_mock=False):
    if _is_online_testing_enabled() and not always_mock:
        return MagicMock()
    return EndpointMocker(base_url=base_url)


class _DoiResolver:
    def __init__(self):
        self.m = _new_endpoint_mocker()

    def __call__(self, doi: str, archive_url: str, status_code: int = 200):
        self.m.start()
        # patch request to doi.org and the resolved URL,
        # because doi_to_url does follow redirects.
        self.m.get(
            f"https://doi.org/{doi}", status_code=302, headers={"Location": archive_url}
        )
        self.m.get(archive_url, status_code=status_code)
        return self

    def __enter__(self):
        pass

    def __exit__(self, type, value, traceback):
        self._stop()

    def _stop(self):
        self.m.reset()
        self.m.stop()


_DOI_RESOLVER = _DoiResolver()


@pytest.fixture
def make_doi_resolve_to():
    yield _DOI_RESOLVER
    _DOI_RESOLVER._stop()  # pylint: disable=protected-access


class _DataRepositoryTester:
    data_repo_class: type[DataRepository] = None
    base_url_fallback: Optional[str] = None

    def __init__(self, base_url: Optional[str] = None):
        self.base_url = _value_or(
            _value_or(base_url, self.base_url_fallback), _random_base_url()
        )
        self._repo = None

        if self.data_repo_class is None:
            raise ValueError("data_repo_class must be provided.")

    def _initialize_repo(
        self, doi: Optional[str] = None, archive_path: Optional[str] = None
    ) -> DataRepository:
        doi = _value_or(doi, _random_doi())
        archive_path = _value_or(archive_path, _random_archive_path())
        return self.data_repo_class.initialize(
            doi, urljoin(self.base_url, archive_path)
        )

    def initialize_repo(self, doi: str, archive_path: str):
        # TODO: decide if reinit is allowed
        if self._repo is not None:
            raise RuntimeError(
                "Repository already initialized. Please use a new DataRepositoryTester."
            )
        self._repo = self._initialize_repo(doi, archive_path)

    @property
    def repo(self):
        if self._repo is None:
            raise RuntimeError(
                "Repository was not initialized. Please call `initialize_repo` first."
            )
        return self._repo

    def assert_repo_does_initialize(
        self, doi: Optional[str] = None, archive_path: Optional[str] = None
    ) -> None:
        assert self._initialize_repo(doi=doi, archive_path=archive_path) is not None

    def assert_repo_does_not_initialize(
        self, doi: Optional[str] = None, archive_path: Optional[str] = None
    ) -> None:
        assert self._initialize_repo(doi=doi, archive_path=archive_path) is None

    def endpoint_mocker(self, always_mock=False):
        return _new_endpoint_mocker(self.base_url, always_mock=always_mock)


@pytest.fixture(scope="session")
def create_data_repo_tester_type():
    def _new(data_repo_type: type, base_url_fallback: Optional[str] = None):
        return type(
            f"{data_repo_type.__name__}Tester",
            (_DataRepositoryTester,),
            {
                "data_repo_class": data_repo_type,
                "base_url_fallback": base_url_fallback,
            },
        )

    return _new


def _do_sanity_check(data_repo_class):
    # here some sanity checks are performed
    # - check that init_requires_requests holds its promise by fuzzing initialize
    # - check that initialize only throws allowed_exceptions
    pass


@pytest.fixture
def sanity_check_data_repo():
    return _do_sanity_check
