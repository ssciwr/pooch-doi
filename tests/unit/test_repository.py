import pytest

from pooch_doi.repository import (
    DataRepository,
    doi_to_url,
    _get_all_available_data_repositories,
)

_VALID_DOIS_TO_URL = (
    ("10.5281/zenodo.17544720", "https://zenodo.org/doi/10.5281/zenodo.17544720", 200),
    (
        "10.6084/m9.figshare.30511304",
        "https://figshare.com/articles/dataset/ab/30511304",
        201,
    ),
)

_INVALID_DOIS_TO_URL = (
    ("10.5281/zenodo.17544720", "https://zenodo.org/doi/10.5281/zenodo.17544720", 403),
    (
        "10.6084/m9.figshare.30511304",
        "https://figshare.com/articles/dataset/ab/30511304",
        404,
    ),
)


@pytest.mark.unit
def test_valid_doi_to_url(doi_mock):
    for doi, archive_url, status_code in _VALID_DOIS_TO_URL:
        with doi_mock(doi, archive_url, status_code=status_code):
            assert doi_to_url(doi) == archive_url


@pytest.mark.unit
def test_invalid_doi_to_url(doi_mock):
    for doi, archive_url, status_code in _INVALID_DOIS_TO_URL:
        with doi_mock(doi, archive_url, status_code=status_code):
            with pytest.raises(ValueError):
                doi_to_url(doi)


class RequestInInitDataRepository(DataRepository):
    init_requires_request = True


class NoRequestInInitDataRepository(DataRepository):
    init_requires_request = False


def test_get_all_available_data_repositories(make_repos_available):
    d1 = RequestInInitDataRepository()
    d2 = NoRequestInInitDataRepository()
    with make_repos_available(d1, d2):
        assert _get_all_available_data_repositories() == [d2, d1]

    with make_repos_available(d2, d1):
        assert _get_all_available_data_repositories() == [d2, d1]

    with make_repos_available():
        assert _get_all_available_data_repositories() == []


def test_doi_to_repository(doi_mock):
    pass
