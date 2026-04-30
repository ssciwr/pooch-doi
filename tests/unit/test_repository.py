import pytest
import logging

from pooch_doi.repository import (
    doi_to_url,
    doi_to_repository,
    _get_all_available_data_repositories,
)


@pytest.mark.parametrize("status_code", [200, 201])
@pytest.mark.unit
def test_doi_to_url_successful_resolution(status_code, dois, make_doi_resolve_to):
    for doi, archive_url in dois.n_valid_doi_to_url_pairs(2):
        with make_doi_resolve_to(doi, archive_url, status_code=status_code):
            assert doi_to_url(doi) == archive_url


@pytest.mark.parametrize("status_code", [403, 404, 500])
@pytest.mark.unit
def test_doi_to_url_failed_resolution(status_code, dois, make_doi_resolve_to):
    for doi, archive_url in dois.n_invalid_doi_to_url_pairs(2):
        with make_doi_resolve_to(doi, archive_url, status_code=status_code):
            with pytest.raises(ValueError):
                doi_to_url(doi)


def test_get_all_available_data_repositories(data_repo_manager, data_repo_factory):
    d1 = data_repo_factory().with_init_requires_requests(True).create_type()
    d2 = data_repo_factory().with_init_requires_requests(False).create_type()
    d3 = data_repo_factory().with_init_requires_requests(False).create_type()

    with data_repo_manager.make_available(d1, d2, d3):
        assert _get_all_available_data_repositories() == [d2, d3, d1]

    with data_repo_manager.make_available(d2, d1, d3):
        assert _get_all_available_data_repositories() == [d2, d3, d1]

    with data_repo_manager.make_available(d1, d3, d2):
        assert _get_all_available_data_repositories() == [d3, d2, d1]

    with data_repo_manager.make_available(d3, d2):
        assert _get_all_available_data_repositories() == [d3, d2]

    with data_repo_manager.make_available(d2):
        assert _get_all_available_data_repositories() == [d2]

    with data_repo_manager.make_available(d1):
        assert _get_all_available_data_repositories() == [d1]

    with data_repo_manager.make_none_available():
        assert _get_all_available_data_repositories() == []


def test_doi_to_repository_with_valid_repo(
    make_doi_resolve_to, data_repo_manager, data_repo_factory
):
    figshare_repo = (
        data_repo_factory().with_initialize.match_domain("figshare.org").create_type()
    )
    zenodo_repo = (
        data_repo_factory().with_initialize.match_domain("zenodo.org").create_type()
    )
    # make figshare first in chain-of-responsibility
    data_repo_manager.make_available(figshare_repo, zenodo_repo)

    doi = "10.5281/zenodo.4924875"
    url = "https://zenodo.org/doi/10.5281/zenodo.4924875"
    make_doi_resolve_to(doi, url)

    assert isinstance(doi_to_repository(doi), zenodo_repo)


def test_doi_to_repository_with_faulty_repo(
    make_doi_resolve_to, data_repo_manager, data_repo_factory, caplog
):
    faulty_repo = data_repo_factory(typename="FaultyRepo")
    faulty_repo = faulty_repo.with_issue_tracker("https://issuetracker.de")
    faulty_repo = faulty_repo.with_allowed_exceptions(())  # no allowed exceptions
    faulty_repo = faulty_repo.with_initialize.raise_exception(
        ValueError("Test Exception")
    )
    faulty_repo = faulty_repo.create_type()
    zenodo_repo = (
        data_repo_factory().with_initialize.match_domain("zenodo.org").create_type()
    )
    # prioritize faulty_repo
    data_repo_manager.make_available(faulty_repo, zenodo_repo)

    doi = "10.5281/zenodo.4924875"
    url = "https://zenodo.org/doi/10.5281/zenodo.4924875"
    make_doi_resolve_to(doi, url)

    caplog.set_level(logging.WARNING, logger="pooch-doi")
    assert isinstance(doi_to_repository(doi), zenodo_repo)
    assert caplog.record_tuples == [
        (
            "pooch-doi",
            logging.WARNING,
            "Repository Implementation 'FaultyRepo' failed with exception: 'Test Exception'. Please open an issue at 'https://issuetracker.de'.",
        )
    ]


def test_doi_to_repository_with_allowed_faulty_repo(
    make_doi_resolve_to, data_repo_manager, data_repo_factory
):
    faulty_repo = data_repo_factory()
    faulty_repo = faulty_repo.with_name.return_value("faulty_repo")
    faulty_repo = faulty_repo.with_issue_tracker("https://issuetracker.de")
    faulty_repo = faulty_repo.with_allowed_exceptions(
        (ValueError,)
    )  # ValueError is allowed
    faulty_repo = faulty_repo.with_initialize.raise_exception(
        ValueError("Test Exception")
    )
    faulty_repo = faulty_repo.create_type()
    zenodo_repo = (
        data_repo_factory().with_initialize.match_domain("zenodo.org").create_type()
    )
    # prioritize faulty_repo
    data_repo_manager.make_available(faulty_repo, zenodo_repo)

    doi = "10.5281/zenodo.4924875"
    url = "https://zenodo.org/doi/10.5281/zenodo.4924875"
    make_doi_resolve_to(doi, url)

    with pytest.raises(ValueError, match="Test Exception"):
        doi_to_repository(doi)


def test_doi_to_repository_with_user_warning(
    make_doi_resolve_to, data_repo_manager, data_repo_factory
):
    figshare_repo = (
        data_repo_factory().with_initialize.match_domain("figshare.org").create_type()
    )
    zenodo_repo = data_repo_factory()
    zenodo_repo = zenodo_repo.with_name.return_value("zenodo_repo")
    zenodo_repo = zenodo_repo.with_user_warning("Test Warning.")
    zenodo_repo = zenodo_repo.with_initialize.match_domain("zenodo.org")
    zenodo_repo = zenodo_repo.create_type()
    # prioritize figshare_repo
    data_repo_manager.make_available(figshare_repo, zenodo_repo)

    doi = "10.5281/zenodo.4924875"
    url = "https://zenodo.org/doi/10.5281/zenodo.4924875"
    make_doi_resolve_to(doi, url)

    with pytest.warns(
        UserWarning,
        match="Selected Repository 'zenodo_repo' issued a warning: Test Warning.",
    ):
        assert isinstance(doi_to_repository(doi), zenodo_repo)
