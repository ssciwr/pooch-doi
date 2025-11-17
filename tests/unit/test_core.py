import pytest
import pooch
import pooch_doi
from pooch_doi.repository import (
    DataRepository,
    doi_to_url,
    _get_all_available_data_repositories,
)

def test_retrieve_from_doi_without_repos_available(mocker, data_repo_manager, make_doi_resolve_to):
    # we assert that retrieve methode works properly so its enough to check
    # if the parameters of the retrieve function are correct
    mock_retrieve = mocker.patch("pooch_doi.core.retrieve")
    doi = "10.5281/zenodo.17544720"
    url = "https://zenodo.org/doi/10.5281/zenodo.17544720"
    # make doi resolve to a valid url
    make_doi_resolve_to(doi, url)
    # make zero repos available
    data_repo_manager.make_none_available()
    with pytest.raises(ValueError):
        pooch_doi.retrieve_from_doi(doi, known_hash="hash", filename="result_values",path=None, processor=None, downloader=None,progressbar=False)
    mock_retrieve.assert_not_called()

def test_retrieve_from_doi_with_repos_available(mocker, data_repo_factory, data_repo_manager, make_doi_resolve_to):
    # we assert that retrieve methode works properly so its enough to check
    # if the parameters of the retrieve function are correct
    mock_retrieve = mocker.patch("pooch_doi.core.retrieve")
    doi = "10.5281/zenodo.17544720"
    url = "https://zenodo.org/doi/10.5281/zenodo.17544720"
    # make doi resolve to a valid url
    make_doi_resolve_to(doi, url)

    # craft a fake repo and make it available
    d1 = data_repo_factory().with_base_impl()
    d1 = d1.with_download_url.return_value(url)
    d1 = d1.with_initialize.match_domain("zenodo.org")
    d1 = d1.create_instance()
    data_repo_manager.make_available(d1)

    pooch_doi.retrieve_from_doi(doi, known_hash="hash", filename="result_values",path=None, processor=None, downloader=None,progressbar=False)
    mock_retrieve.assert_called_once_with(url, "hash", "result_values", None, None, None, False)