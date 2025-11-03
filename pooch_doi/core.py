from typing import Optional, override

from pooch import Pooch, retrieve
from .repository import doi_to_repository
from .utils import parse_doi


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
        pass

    @override
    def load_registry_from_doi(self):
        # Create a repository instance
        doi_netloc, _ = parse_doi(self.base_url)
        data_repository = doi_to_repository(doi_netloc)

        # Call registry population for this repository
        data_repository.populate_registry(self)

    @override
    def is_available(self, fname, downloader=None):
        self._assert_file_in_registry(fname)
        # We stay aligned with the current implementation of pooch which
        # does not support availability checks for DOIDownloader
        # TODO: this could potentially be improved by using the availability feature of HTTPDownloader
        raise NotImplementedError("DOIPooch does not support availability checks.")


def retrieve_from_doi(
    doi: str,
    known_hash: Optional[str] = None,
    fname: Optional[str] = None,
    path=None,
    processor=None,
    downloader=None,
    progressbar: bool = False,
) -> str:
    # Resolve DOI
    doi_netloc, doi_path = parse_doi(doi)
    data_repository = doi_to_repository(doi_netloc)

    # Remove the leading slash in the path and
    # resolve the download URL
    if doi_path[0] == "/":
        doi_path = doi_path[1:]
    download_url = data_repository.download_url(doi_path)

    # Retrieve actual data file(s)
    return retrieve(
        download_url, known_hash, fname, path, processor, downloader, progressbar
    )
