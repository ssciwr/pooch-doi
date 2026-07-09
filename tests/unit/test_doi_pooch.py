import pytest
import pathlib
import doiggie
from doiggie.license import *

doi = "10.5281/zenodo.4924875"
archive_url = "https://zenodo.org/doi/10.5281/zenodo.4924875"
download_url = "https://zenodo.org/api/records/4924875/files/tiny-data.txt/content"


class OfflineDownloader:
    def __init__(self, filepath: str):
        self.filepath = (
            pathlib.Path(__file__).absolute().parent.parent / "data" / filepath
        )
        self.latest_call = ("", None, False)

    def __call__(
        self, url, output_file, pooch, check_only=False
    ):  # pylint: disable=R0914
        self.latest_call = (url, pooch, check_only)

        if check_only:
            return self.filepath.exists()

        ispath = not hasattr(output_file, "write")
        if ispath:
            # pylint: disable=consider-using-with
            output_file = open(output_file, "w+b")
            # pylint: enable=consider-using-with

        output_file.write(self.filepath.read_bytes())
        output_file.flush()

        if ispath:
            output_file.close()

        return None


def does_file_match_data_file(filepath: str, data_filepath: str) -> bool:
    f1 = pathlib.Path(filepath)
    datafile = pathlib.Path(__file__).absolute().parent.parent / "data" / data_filepath
    return f1.read_bytes() == datafile.read_bytes()


def test_doi_pooch_fetch_with_registry(
    tempdir, data_repo_factory, data_repo_manager, make_doi_resolve_to
):
    # make doi resolve to a valid url
    make_doi_resolve_to(doi, archive_url)

    # craft a fake repo and make it available
    d1 = data_repo_factory()
    d1 = d1.with_download_url.return_value(download_url)
    d1 = d1.with_initialize.match_domain("zenodo.org")
    d1 = d1.create_type()
    data_repo_manager.make_available(d1)

    doi_pooch = doiggie.DOIPooch(
        path=tempdir,
        doi=doi,
        registry={
            "tiny-data.txt": "md5:70e2afd3fd7e336ae478b1e740a5f08e",
            "store.zip": "md5:7008231125631739b64720d1526619ae",
        },
    )

    downloader = OfflineDownloader("dataset/tiny-data.txt")
    fname = doi_pooch.fetch("tiny-data.txt", downloader=downloader)
    assert downloader.latest_call == (download_url, doi_pooch, False)
    assert does_file_match_data_file(fname, "dataset/tiny-data.txt")


def test_doi_pooch_fetch_with_populate_registry(
    tempdir, data_repo_factory, data_repo_manager, make_doi_resolve_to
):
    # make doi resolve to a valid url
    make_doi_resolve_to(doi, archive_url)

    # craft a fake repo and make it available
    d1 = data_repo_factory()
    d1 = d1.with_download_url.return_value(download_url)
    d1 = d1.with_create_registry.return_value(
        {
            "tiny-data.txt": "md5:70e2afd3fd7e336ae478b1e740a5f08e",
            "store.zip": "md5:7008231125631739b64720d1526619ae",
        }
    )
    d1 = d1.with_initialize.match_domain("zenodo.org")
    d1 = d1.create_type()
    data_repo_manager.make_available(d1)

    doi_pooch = doiggie.DOIPooch(
        path=tempdir,
        doi=doi,
        populate_registry=True,
    )

    downloader = OfflineDownloader("dataset/tiny-data.txt")
    fname = doi_pooch.fetch("tiny-data.txt", downloader=downloader)
    assert downloader.latest_call == (download_url, doi_pooch, False)
    assert does_file_match_data_file(fname, "dataset/tiny-data.txt")


def test_doi_pooch_fetch_with_load_registry_from_doi(
    tempdir, data_repo_factory, data_repo_manager, make_doi_resolve_to
):
    # make doi resolve to a valid url
    make_doi_resolve_to(doi, archive_url)

    # craft a fake repo and make it available
    d1 = data_repo_factory()
    d1 = d1.with_download_url.return_value(download_url)
    d1 = d1.with_create_registry.return_value(
        {
            "tiny-data.txt": "md5:70e2afd3fd7e336ae478b1e740a5f08e",
            "store.zip": "md5:7008231125631739b64720d1526619ae",
        }
    )
    d1 = d1.with_initialize.match_domain("zenodo.org")
    d1 = d1.create_type()
    data_repo_manager.make_available(d1)

    doi_pooch = doiggie.DOIPooch(
        path=tempdir,
        doi=doi,
    )
    doi_pooch.load_registry_from_doi()

    downloader = OfflineDownloader("dataset/tiny-data.txt")
    fname = doi_pooch.fetch("tiny-data.txt", downloader=downloader)
    assert downloader.latest_call == (download_url, doi_pooch, False)
    assert does_file_match_data_file(fname, "dataset/tiny-data.txt")


def test_doi_pooch_is_available(
    tempdir, data_repo_factory, data_repo_manager, make_doi_resolve_to
):
    # make doi resolve to a valid url
    make_doi_resolve_to(doi, archive_url)

    # craft a fake repo and make it available
    d1 = data_repo_factory()
    d1 = d1.with_download_url.return_value(download_url)
    d1 = d1.with_create_registry.return_value(
        {
            "tiny-data.txt": "md5:70e2afd3fd7e336ae478b1e740a5f08e",
            "store.zip": "md5:7008231125631739b64720d1526619ae",
        }
    )
    d1 = d1.with_initialize.match_domain("zenodo.org")
    d1 = d1.create_type()
    data_repo_manager.make_available(d1)

    doi_pooch = doiggie.DOIPooch(
        path=tempdir,
        doi=doi,
        populate_registry=True,
    )

    # TESTCASE 1: File in registry and available
    downloader = OfflineDownloader("dataset/tiny-data.txt")
    assert doi_pooch.is_available("tiny-data.txt", downloader=downloader)
    assert downloader.latest_call == (download_url, doi_pooch, True)

    # TESTCASE 2: File in registry and not available
    downloader = OfflineDownloader("dataset/tiny-data-non-existent.txt")
    assert not doi_pooch.is_available("tiny-data.txt", downloader=downloader)
    assert downloader.latest_call == (download_url, doi_pooch, True)

    # TESTCASE 3: File not in registry
    with pytest.raises(
        ValueError, match="File 'tiny-data-non-existent.txt' is not in the registry."
    ):
        doi_pooch.is_available("tiny-data-non-existent.txt")


def test_doi_pooch_get_url(
    tempdir, data_repo_factory, data_repo_manager, make_doi_resolve_to
):
    # make doi resolve to a valid url
    make_doi_resolve_to(doi, archive_url)

    # craft a fake repo and make it available
    d1 = data_repo_factory()
    d1 = d1.with_download_url.return_value(download_url)
    d1 = d1.with_create_registry.return_value(
        {
            "tiny-data.txt": "md5:70e2afd3fd7e336ae478b1e740a5f08e",
            "store.zip": "md5:7008231125631739b64720d1526619ae",
        }
    )
    d1 = d1.with_initialize.match_domain("zenodo.org")
    d1 = d1.create_type()
    data_repo_manager.make_available(d1)

    doi_pooch = doiggie.DOIPooch(
        path=tempdir,
        doi=doi,
        populate_registry=True,
    )

    # TESTCASE 1: File in registry
    assert doi_pooch.get_url("tiny-data.txt") == download_url

    # TESTCASE 2: File not in registry
    with pytest.raises(
        ValueError, match="File 'tiny-data-non-existent.txt' is not in the registry."
    ):
        doi_pooch.get_url("tiny-data-non-existent.txt")


def test_doi_pooch_licenses(
    tempdir, data_repo_factory, data_repo_manager, make_doi_resolve_to
):
    test_license = License(
        name="Other (Public Domain)",
        description="License one",
        copyright="2026 The Authors",
    )

    # make doi resolve to a valid url
    make_doi_resolve_to(doi, archive_url)

    # craft a fake repo and make it available
    d1 = data_repo_factory()
    d1 = d1.with_download_url.return_value(download_url)
    d1 = d1.with_create_registry.return_value(
        {
            "tiny-data.txt": "md5:70e2afd3fd7e336ae478b1e740a5f08e",
            "store.zip": "md5:7008231125631739b64720d1526619ae",
        }
    )
    d1 = d1.with_licenses.return_value([test_license])
    d1 = d1.with_initialize.match_domain("zenodo.org")
    d1 = d1.create_type()
    data_repo_manager.make_available(d1)

    doi_pooch = doiggie.DOIPooch(
        path=tempdir,
        doi=doi,
        populate_registry=True,
    )

    assert doi_pooch.licenses() == [test_license]
