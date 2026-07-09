from typing import Optional
from functools import cached_property
from pooch import Pooch, retrieve
from .repository import doi_to_repository
from .utils import assert_valid_doi


class DOIPooch(Pooch):
    def __init__(self, path: str, doi: str, **kwargs):
        populate_registry = kwargs.pop("populate_registry", False)
        self.doi = doi
        super().__init__(path, doi, **kwargs)

        if populate_registry:
            self.load_registry_from_doi()

    @cached_property
    def data_repository(self):
        assert_valid_doi(self.doi)
        return doi_to_repository(self.doi)

    def get_url(self, fname):
        super()._assert_file_in_registry(fname)
        return self.data_repository.download_url(fname)

    def load_registry_from_doi(self):
        # Update registry for this repository
        self.registry = self.data_repository.create_registry()

    def licenses(self):
        return self.data_repository.licenses()


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
    assert_valid_doi(doi)
    data_repository = doi_to_repository(doi)

    # use file-hash from registry if no known_hash is provided
    if known_hash is None:
        registry = data_repository.create_registry()
        if filename not in registry:
            raise ValueError(
                f"Could not find hash for file '{filename}' in registry and no known_hash provided."
            )
        known_hash = registry[filename]

    # Resolve the download URL
    download_url = data_repository.download_url(filename)

    # Retrieve actual data file(s)
    return retrieve(
        download_url, known_hash, filename, path, processor, downloader, progressbar
    )
