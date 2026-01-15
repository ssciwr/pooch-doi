import functools
from typing import Optional
from functools import cached_property

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
        self.doi = doi
        super().__init__(path, doi, **kwargs)

        # TODO: maybe ensure doi is no other protocol

        if populate_registry:
            self.load_registry_from_doi()
    
    @cached_property
    def data_repository(self):
        assert_valid_doi(self.doi)
        return doi_to_repository(self.doi)

    def download_url(self, fname):
        return self.data_repository.download_url(fname)
    
    def get_url(self, fname):
        return self.download_url(fname)

    @override
    def load_registry_from_doi(self):
        # Create a repository instance
        assert_valid_doi(self.base_url)
        data_repository = doi_to_repository(self.base_url)

        # Update registry for this repository
        self.registry = data_repository.create_registry()

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
            raise ValueError(f"File '{filename}' not found in registry.")
        known_hash = registry[filename]

    # Resolve the download URL
    download_url = data_repository.download_url(filename)

    # Retrieve actual data file(s)
    return retrieve(
        download_url, known_hash, filename, path, processor, downloader, progressbar
    )
