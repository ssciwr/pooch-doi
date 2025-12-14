import pytest

from pooch_doi.repository import (
    doi_to_url,
    doi_to_repository,
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

def test_doi_to_repository_with_supported_repository(data_repo_manager, data_repo_factory, make_doi_resolve_to):
    doi = "zenodo/abc"
    
    # mock everything needed
    d1 = data_repo_factory().with_base_impl()
    d1 = d1.with_initialize.match_domain("zenodo.org")
    t = d1.create_type()
    data_repo_manager.make_available(t)
    make_doi_resolve_to(doi, "https://zenodo.org/records/abc", status_code=200)
    
    assert isinstance(doi_to_repository(doi), t)

def test_doi_to_repository_without_supported_repository(data_repo_manager, data_repo_factory, dois): 
    # mock everything needed
    # Todo: ensure repositorz is not supported, ValueError can be more specified
    with pytest.raises(ValueError): 
        doi_to_repository(dois.one_invalid_doi)
    

def test_doi_to_repository_with_invalid_doi_and_supported_repository(data_repo_manager, data_repo_factory, dois): 
    # mock everything needed
    # Todo: ensure repositorz is supported
    with pytest.raises(ValueError):
        doi_to_repository(dois.one_invalid_doi)

