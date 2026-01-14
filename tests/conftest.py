from typing import Tuple, Callable
import pytest
from unittest.mock import MagicMock, patch
from urllib.parse import urlsplit

from pooch_doi import DataRepository


# This class can be used to specifically make a set of mock data repositories available.
# It can be used as a function call or a context manager.
class _DataRepoManager:
    class _PatchContext:
        def __init__(self, manager: "_DataRepoManager"):
            self.manager = manager

        def __enter__(self):
            pass

        def __exit__(self, type, value, traceback):
            self.manager._unpatch()

    def __init__(self):
        self.entries = []
        self.patcher = patch("importlib.metadata.entry_points")

    def make_none_available(self):
        self._patch()
        return _DataRepoManager._PatchContext(self)

    def make_available(self, first_repo, *additional_repos):
        self._patch(first_repo, *additional_repos)
        return _DataRepoManager._PatchContext(self)

    def _patch(self, *repos):
        self.entries = [MagicMock() for _ in repos]
        for e, r in zip(self.entries, repos):
            e.load.return_value = r

        mock = self.patcher.start()
        mock.return_value = self.entries

    def _unpatch(self):
        self.patcher.stop()


_DATA_REPO_MANAGER = _DataRepoManager()


@pytest.fixture
def data_repo_manager():
    yield _DATA_REPO_MANAGER
    _DATA_REPO_MANAGER._unpatch()  # pylint: disable=protected-access


class _DataRepoFactory:
    # This class is used to provide a default implementation for all methods in `DataRepository`
    # that would otherwise throw an error.
    class _BaseImplDataRepository(DataRepository):
        @property
        def name(self):
            return "BaseImplDataRepository"

        @property
        def homepage(self):
            return "homepage"

        @classmethod
        def initialize(cls, doi, archive_url):
            return None

        def licenses(self):
            return []

        def download_url(self, file_name):
            return "download_url"

        def create_registry(self):
            return {}

    def __init__(self):
        self.dict = dict()
        self.base = _DataRepoFactory._BaseImplDataRepository
        self._provide_method_factories()

    def _with_attribute(self, attribute: str, value) -> "_DataRepoFactory":
        self.dict[attribute] = value
        return self

    # ================================================================
    # Class attribute setters

    def with_issue_tracker(self, issue_tracker: str) -> "_DataRepoFactory":
        return self._with_attribute("issue_tracker", issue_tracker)

    def with_allows_self_hosting(self, allows_self_hosting: bool) -> "_DataRepoFactory":
        return self._with_attribute("allows_self_hosting", allows_self_hosting)

    def with_full_support(self, full_support: bool) -> "_DataRepoFactory":
        return self._with_attribute("full_support", full_support)

    def with_user_warning(self, user_warning: str) -> "_DataRepoFactory":
        return self._with_attribute("user_warning", user_warning)

    def with_init_requires_requests(
        self, init_requires_requests: bool
    ) -> "_DataRepoFactory":
        return self._with_attribute("init_requires_requests", init_requires_requests)

    # ================================================================
    # Class method factories

    # This Base class should be the last in MRO, in order for the mixins to work properly!
    class _BaseMethodFactory:
        _method_name: str = "<method>"
        _decorator = None

        def __init__(self, repo_factory: "_DataRepoFactory") -> None:
            self._repo_factory = repo_factory

        def _set(self, func: Callable) -> "_DataRepoFactory":
            if self._decorator is not None:
                func = self._decorator(func)
            return self._repo_factory._with_attribute(self._method_name, func)

    class _FuncStrategyMixin:
        def func(self, func: Callable) -> "_DataRepoFactory":
            return super()._set(func)

    class _ReturnValueStrategyMixin:
        def return_value(self, value) -> "_DataRepoFactory":
            return super()._set(lambda *args, **kwargs: value)

    class _RaiseExceptionStrategyMixin:
        def raise_exception(self, exc: Exception):
            def _func(*args, **kwargs):
                raise exc

            return super()._set(_func)

    class _NameMethod(
        _FuncStrategyMixin,
        _ReturnValueStrategyMixin,
        _RaiseExceptionStrategyMixin,
        _BaseMethodFactory,
    ):
        _method_name = "name"
        _decorator = property

    class _HomepageMethod(
        _FuncStrategyMixin,
        _ReturnValueStrategyMixin,
        _RaiseExceptionStrategyMixin,
        _BaseMethodFactory,
    ):
        _method_name = "homepage"
        _decorator = property

    class _InitializeMethod(
        _FuncStrategyMixin,
        _ReturnValueStrategyMixin,
        _RaiseExceptionStrategyMixin,
        _BaseMethodFactory,
    ):
        _method_name = "initialize"
        _decorator = classmethod

        def match_domain(self, domain: str) -> "_DataRepoFactory":
            def _initialize_match_domain(cls, doi, archive_url):
                return cls() if urlsplit(archive_url).netloc == domain else None

            return self._set(_initialize_match_domain)

    class _DownloadURLMethod(
        _FuncStrategyMixin,
        _ReturnValueStrategyMixin,
        _RaiseExceptionStrategyMixin,
        _BaseMethodFactory,
    ):
        _method_name = "download_url"

    class _CreateRegistryMethod(
        _FuncStrategyMixin,
        _ReturnValueStrategyMixin,
        _RaiseExceptionStrategyMixin,
        _BaseMethodFactory,
    ):
        _method_name = "create_registry"

    def _provide_method_factories(self):
        self.with_name = _DataRepoFactory._NameMethod(self)
        self.with_homepage = _DataRepoFactory._HomepageMethod(self)
        self.with_initialize = _DataRepoFactory._InitializeMethod(self)
        self.with_download_url = _DataRepoFactory._DownloadURLMethod(self)
        self.with_create_registry = _DataRepoFactory._CreateRegistryMethod(self)

    # ================================================================
    # Class creation methods

    def create_type(self) -> type:
        return type("FakeDataRepository", (self.base,), self.dict)

    def create_instance(self) -> type[DataRepository]:
        return self.create_type()()


@pytest.fixture
def data_repo_factory():
    def new_data_repo_factory() -> _DataRepoFactory:
        return _DataRepoFactory()

    return new_data_repo_factory


_VALID_DOI_TO_URL_PAIRS = (
    ("10.5281/zenodo.17544720", "https://zenodo.org/doi/10.5281/zenodo.17544720"),
    (
        "10.6084/m9.figshare.30511304",
        "https://figshare.com/articles/dataset/ab/30511304",
    ),
    (
        "10.71775/kth.eryb7-xe747",
        "https://datarepository.kth.se/doi/10.71775/kth.eryb7-xe747",
    ),
    (
        "10.48436/4pksk-8t382",
        "https://researchdata.tuwien.ac.at/doi/10.48436/4pksk-8t382",
    ),
    (
        "10.23728/b2share.vzgtb-mze32",
        " https://b2share.eudat.eu/doi/10.23728/b2share.vzgtb-mze32",
    ),
    (
        "10.18131/g3-87fa-bg46",
        "https://prism.northwestern.edu/records/dsha7-p3p60",
    ),
    (
        "10.22002/7vcz4-d4p68",
        "https://data.caltech.edu/doi/10.22002/7vcz4-d4p68",
    ),
)
_INVALID_DOI_TO_URL_PAIRS = (
    (
        "11.5281/zenodo.17544720",  # invalid because of wrong prefix
        "https://zenodo.org/doi/11.5281/zenodo.17544720",
    ),
    (
        "10.0/m9.figshare.30511304",  # invalid because prefix only contains one number
        "https://figshare.com/articles/dataset/ab/30511304",
    ),
    (
        "10. 775/kth.eryb7-xe747",  # invalid because of whitspace in prefix
        "https://datarepository.kth.se/doi/10. 775/kth.eryb7-xe747",
    ),
    (
        "10.48436/",  # invalid because suffix is empty
        "https://researchdata.tuwien.ac.at/doi/10.48436/",
    ),
    (
        "10237/28/b2share.vzgtb-mze32",  # invalid because of missing '.' after prefix 10
        " https://b2share.eudat.eu/doi/1023728/b2share.vzgtb-mze32",
    ),
    (
        "10.18131\\g3-87fa-/bg46",  # invalid because of backslash instead of forwoard slash
        "https://prism.northwestern.edu/records/dsha7-p3p60",
    ),
)
_VALID_DOIS = tuple(doi for doi, _ in _VALID_DOI_TO_URL_PAIRS)
_INVALID_DOIS = tuple(doi for doi, _ in _INVALID_DOI_TO_URL_PAIRS)


class _Dois:
    @staticmethod
    def all_valid_dois() -> Tuple[str, ...]:
        return _VALID_DOIS

    @staticmethod
    def all_invalid_dois() -> Tuple[str, ...]:
        return _INVALID_DOIS

    @staticmethod
    def n_valid_dois(n: int):
        return _Dois.all_valid_dois()[:n]

    @staticmethod
    def n_invalid_dois(n: int):
        return _Dois.all_invalid_dois()[:n]

    @staticmethod
    def one_valid_doi():
        return _Dois.n_valid_dois(1)[0]

    @staticmethod
    def one_invalid_doi():
        return _Dois.n_invalid_dois(1)[0]

    @staticmethod
    def all_valid_doi_to_url_pairs() -> Tuple[Tuple[str, str], ...]:
        return _VALID_DOI_TO_URL_PAIRS

    @staticmethod
    def all_invalid_doi_to_url_pairs() -> Tuple[Tuple[str, str], ...]:
        return _INVALID_DOI_TO_URL_PAIRS

    @staticmethod
    def n_valid_doi_to_url_pairs(n: int):
        return _Dois.all_valid_doi_to_url_pairs()[:n]

    @staticmethod
    def n_invalid_doi_to_url_pairs(n: int):
        return _Dois.all_invalid_doi_to_url_pairs()[:n]

    @staticmethod
    def one_valid_doi_to_url_pair():
        return _Dois.n_valid_doi_to_url_pairs(1)[0]

    @staticmethod
    def one_invalid_doi_to_url_pair():
        return _Dois.n_invalid_doi_to_url_pairs(1)[0]


@pytest.fixture
def dois():
    return _Dois


# Pytest fixtures from test_utils
from pooch_doi.test_utils.repository import make_doi_resolve_to


def pytest_configure(config):
    config.addinivalue_line("markers", "slow: marks tests as slow")
    config.addinivalue_line("markers", "unit: marks tests as unit tests")
    config.addinivalue_line("markers", "integration: marks tests as integration test")
