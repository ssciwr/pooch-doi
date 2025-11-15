import pytest

from pooch_doi.repository import (
    doi_to_url,
    _get_all_available_data_repositories,
)


@pytest.mark.parametrize("status_code", [200,201])
@pytest.mark.unit
def test_doi_to_url_successful_resolution(status_code, dois, make_doi_resolve_to):
    for doi, archive_url in dois.n_valid_doi_to_url_pairs(2):
        with make_doi_resolve_to(doi, archive_url, status_code=status_code):
            assert doi_to_url(doi) == archive_url


@pytest.mark.parametrize("status_code", [403,404,500])
@pytest.mark.unit
def test_doi_to_url_failed_resolution(status_code, dois, make_doi_resolve_to):
    for doi, archive_url in dois.n_valid_doi_to_url_pairs(2):
        with make_doi_resolve_to(doi, archive_url, status_code=status_code):
            with pytest.raises(ValueError):
                doi_to_url(doi)


def test_get_all_available_data_repositories(data_repo_manager, data_repo_factory):
    d1 = data_repo_factory().with_init_requires_requests(True).create_instance()
    d2 = data_repo_factory().with_init_requires_requests(False).create_instance()

    with data_repo_manager.make_available(d1, d2):
        assert _get_all_available_data_repositories() == [d2, d1]

    with data_repo_manager.make_available(d2, d1):
        assert _get_all_available_data_repositories() == [d2, d1]

    with data_repo_manager.make_available(d1):
        assert _get_all_available_data_repositories() == [d1]

    with data_repo_manager.make_none_available():
        assert _get_all_available_data_repositories() == []


def test_doi_to_repository():
    pass
