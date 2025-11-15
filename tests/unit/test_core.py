import pytest
import pooch
import pooch_doi
from pooch_doi.repository import (
    DataRepository,
    doi_to_url,
    _get_all_available_data_repositories,
)

def test_retrieve_from_doi_without_repos_available(mocker,make_repos_available,doi_mock):
    # we assert that retrieve methode works properly so its enough to check
    # if the parameters of the retrieve function are correct
    mock_retrieve = mocker.patch("pooch_doi.core.retrieve")
    doi = "10.5281/zenodo.17544720"
    url = "https://zenodo.org/doi/10.5281/zenodo.17544720"
    # make doi resolve to a valid url
    with doi_mock(doi, url):
        # make zero repos available
        make_repos_available()
        with pytest.raises(ValueError):
            pooch_doi.retrieve_from_doi(doi, known_hash="hash", filename="result_values",path=None, processor=None, downloader=None,progressbar=False)
        mock_retrieve.assert_not_called()

def test_retrieve_from_doi_with_repos_available(mocker,make_repos_available,doi_mock):
    # we assert that retrieve methode works properly so its enough to check
    # if the parameters of the retrieve function are correct
    mock_retrieve = mocker.patch("pooch_doi.core.retrieve")
    doi = "10.5281/zenodo.17544720"
    url = "https://zenodo.org/doi/10.5281/zenodo.17544720"
    # make doi resolve to a valid url
    with doi_mock(doi, url):
        d1 = DataRepository()
        make_repos_available(d1)
        # patch doi_to_repository to skip chain of responsiblity and return our fakerepo
        mocker.patch("pooch_doi.core.doi_to_repository",return_value = d1)
        # patch fakerepo classmethode download_url to return our url
        mocker.patch.object(d1, "download_url", return_value = url)
        pooch_doi.retrieve_from_doi(doi, known_hash="hash", filename="result_values",path=None, processor=None, downloader=None,progressbar=False)
        mock_retrieve.assert_called_once_with(url, "hash", "result_values", None, None, None, False)