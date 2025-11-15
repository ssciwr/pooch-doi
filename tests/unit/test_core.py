import pytest
import pooch
import pooch_doi

def test_retrieve_from_doi_without_repos_available(mocker,make_repos_available,doi_mock):
    # we assert that retrieve methode works properly so its enough to check
    # if the parameters of the retrieve function are correct
    mocker.patch("pooch.retrieve")
    doi = "10.5281/zenodo.17544720"
    url = "https://zenodo.org/doi/10.5281/zenodo.17544720"
    # make doi resolve to a valid url
    with doi_mock(doi, url):
        # make zero repos available
        make_repos_available()
        with pytest.raises(ValueError):
            pooch_doi.retrieve_from_doi(doi, known_hash="hash", filename="result_values",path=None, processor=None, downloader=None,progressbar=False)
        pooch.retrieve.assert_not_called()
