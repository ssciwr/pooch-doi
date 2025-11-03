from typing import override

from pooch import Pooch
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
