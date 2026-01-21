import pytest
import pooch_doi


def test_retrieve_from_doi_without_repos_available(
    mocker, data_repo_manager, make_doi_resolve_to
):
    # we assert that retrieve methode works properly so its enough to check
    # if the parameters of the retrieve function are correct
    mock_retrieve = mocker.patch("pooch_doi.core.retrieve")
    doi = "10.5281/zenodo.4924875"
    url = "https://zenodo.org/doi/10.5281/zenodo.4924875"
    # make doi resolve to a valid url
    make_doi_resolve_to(doi, url)
    # make zero repos available
    data_repo_manager.make_none_available()
    with pytest.raises(ValueError, match="Invalid data repository 'zenodo.org'"):
        pooch_doi.retrieve_from_doi(
            doi,
            known_hash="hash",
            filename="result_values",
            path=None,
            processor=None,
            downloader=None,
            progressbar=False,
        )
    mock_retrieve.assert_not_called()


def test_retrieve_from_doi_with_repos_available(
    mocker, data_repo_factory, data_repo_manager, make_doi_resolve_to
):
    mock_retrieve = mocker.patch("pooch_doi.core.retrieve")
    doi = "10.5281/zenodo.4924875"
    url = "https://zenodo.org/doi/10.5281/zenodo.4924875"
    # make doi resolve to a valid url
    make_doi_resolve_to(doi, url)

    # craft a fake repo and make it available
    d1 = data_repo_factory()
    d1 = d1.with_download_url.return_value(url)
    d1 = d1.with_initialize.match_domain("zenodo.org")
    d1 = d1.create_type()
    data_repo_manager.make_available(d1)

    pooch_doi.retrieve_from_doi(
        doi,
        known_hash="hash",
        filename="result_values",
        path=None,
        processor=None,
        downloader=None,
        progressbar=False,
    )
    mock_retrieve.assert_called_once_with(
        url, "hash", "result_values", None, None, None, False
    )


def test_retrieve_from_doi_with_invalid_doi(
    mocker, data_repo_factory, data_repo_manager, make_doi_resolve_to
):
    mock_retrieve = mocker.patch("pooch_doi.core.retrieve")
    # doi is invalid:
    doi = "11.5281/zenodo.4924875"
    url = "https://zenodo.org/doi/11.5281/zenodo.4924875"
    # make doi resolve to a valid url
    make_doi_resolve_to(doi, url)

    # craft a fake repo and make it available
    d1 = data_repo_factory()
    d1 = d1.with_download_url.return_value(url)
    d1 = d1.with_initialize.match_domain("zenodo.org")
    d1 = d1.create_type()
    data_repo_manager.make_available(d1)

    with pytest.raises(ValueError, match=f"Invalid DOI: {doi!s}"):
        pooch_doi.retrieve_from_doi(
            doi,
            known_hash="hash",
            filename="result_values",
            path=None,
            processor=None,
            downloader=None,
            progressbar=False,
        )
    mock_retrieve.assert_not_called()


def test_retrieve_from_doi_without_hash(
    mocker, data_repo_factory, data_repo_manager, make_doi_resolve_to
):
    mock_retrieve = mocker.patch("pooch_doi.core.retrieve")
    doi = "10.5281/zenodo.4924875"
    url = "https://zenodo.org/doi/10.5281/zenodo.4924875"
    # make doi resolve to a valid url
    make_doi_resolve_to(doi, url)

    # craft a fake repo and make it available
    d1 = data_repo_factory()
    d1 = d1.with_download_url.return_value(url)
    d1 = d1.with_initialize.match_domain("zenodo.org")
    d1 = d1.with_create_registry.return_value({"file1": "file1_hash"})
    d1 = d1.create_type()
    data_repo_manager.make_available(d1)

    pooch_doi.retrieve_from_doi(
        doi,
        known_hash=None,
        filename="file1",
        path=None,
        processor=None,
        downloader=None,
        progressbar=False,
    )
    mock_retrieve.assert_called_once_with(
        url, "file1_hash", "file1", None, None, None, False
    )


def test_retrieve_from_doi_without_hash_and_non_existent_file(
    mocker, data_repo_factory, data_repo_manager, make_doi_resolve_to
):
    mock_retrieve = mocker.patch("pooch_doi.core.retrieve")
    doi = "10.5281/zenodo.4924875"
    url = "https://zenodo.org/doi/10.5281/zenodo.4924875"
    # make doi resolve to a valid url
    make_doi_resolve_to(doi, url)

    # craft a fake repo and make it available
    d1 = data_repo_factory()
    d1 = d1.with_download_url.return_value(url)
    d1 = d1.with_initialize.match_domain("zenodo.org")
    d1 = d1.with_create_registry.return_value({"file1": "file1_hash"})
    d1 = d1.create_type()
    data_repo_manager.make_available(d1)

    with pytest.raises(
        ValueError,
        match="Could not find hash for file 'file2' in registry and no known_hash provided",
    ):
        pooch_doi.retrieve_from_doi(
            doi,
            known_hash=None,
            filename="file2",
            path=None,
            processor=None,
            downloader=None,
            progressbar=False,
        )
    mock_retrieve.assert_not_called()
