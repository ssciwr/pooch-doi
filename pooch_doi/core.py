import functools
from typing import Optional

try:
    from typing import override
except ImportError:
    # dummy override decorator
    from functools import update_wrapper

    def override(func):
        return functools.update_wrapper(
            lambda *args, **kwargs: func(*args, **kwargs), func
        )


from pooch import Pooch, retrieve
from .repository import doi_to_repository
from .utils import parse_doi, assert_valid_doi


class DOIPooch(Pooch):
    def __init__(self, path: str, doi: str, **kwargs):
        populate_registry = kwargs.pop("populate_registry", False)
        super().__init__(path, doi, **kwargs)

        # TODO: maybe ensure doi is no other protocol

        if populate_registry:
            self.load_registry_from_doi()

    @override
    def fetch(self, fname, processor=None, downloader=None, progressbar=False):
        # TODO: fetch file. see `Pooch.fetch`
        # TODO: resolve DOI, use HTTPSDownloader, cache data repositori
        pass

    @override
    def load_registry_from_doi(self):
        # Create a repository instance
        assert_valid_doi(self.base_url)
        data_repository = doi_to_repository(self.base_url)

        # Update registry for this repository
        self.registry = data_repository.create_registry()

    @override
    def is_available(self, fname, downloader=None):
        self._assert_file_in_registry(fname)
        # We stay aligned with the current implementation of pooch which
        # does not support availability checks for DOIDownloader
        # TODO: this could potentially be improved by using the availability feature of HTTPDownloader
        raise NotImplementedError("DOIPooch does not support availability checks.")


def retrieve_from_doi(
    doi: str,
    filename: str,
    known_hash: Optional[str] = None,
    path=None,
    processor=None,
    downloader=None,
    progressbar: bool = False,
) -> str:
    # Resolve DOI
    print("In retrieve from doi methode")
    assert_valid_doi(doi)
    data_repository = doi_to_repository(doi)

    # use file-hash from registry if no known_hash is provided
    if known_hash is None:
        registry = data_repository.create_registry()
        if filename not in registry:
            raise ValueError(f"File '{filename}' not found in registry.")
        known_hash = registry[filename]

    # Resolve the download URL
    download_url = data_repository.download_url(doi)

    # Retrieve actual data file(s)
    # Todo: Patch this function for test purpose
    print(download_url)
    return retrieve(
        download_url, known_hash, filename, path, processor, downloader, progressbar
    )
