import importlib.metadata
from typing import Optional, Dict
from .utils import get_logger

DEFAULT_TIMEOUT = 30


def doi_to_url(doi):
    """
    Follow a DOI link to resolve the URL of the archive.

    Parameters
    ----------
    doi : str
        The DOI of the archive.

    Returns
    -------
    url : str
        The URL of the archive in the data repository.

    """
    # Lazy import requests to speed up import time
    import requests  # pylint: disable=C0415

    # Use doi.org to resolve the DOI to the repository website.
    response = requests.get(f"https://doi.org/{doi}", timeout=DEFAULT_TIMEOUT)
    url = response.url
    if 400 <= response.status_code < 600:
        raise ValueError(
            f"Archive with doi:{doi} not found (see {url}). Is the DOI correct?"
        )
    return url


def _get_all_available_data_repositories():
    repositories = [
        ep.load() for ep in importlib.metadata.entry_points(group="data_repositories")
    ]
    # Prioritize repositories that don't make a request in `initialize`.
    repositories.sort(key=lambda repo: int(repo.init_requires_requests))
    return repositories


def doi_to_repository(doi):
    """
    Instantiate a data repository instance from a given DOI.

    This function implements the chain of responsibility dispatch
    to the correct data repository class.

    Parameters
    ----------
    doi : str
        The DOI of the archive.

    Returns
    -------
    data_repository : DataRepository
        The data repository object
    """

    repositories = _get_all_available_data_repositories()

    # Extract the DOI and the repository information
    archive_url = doi_to_url(doi)

    # Try the converters one by one until one of them returned a URL
    data_repository = None
    for repo in repositories:
        try:
            data_repository = repo.initialize(
                archive_url=archive_url,
                doi=doi,
            )
            if data_repository is not None:
                break
        except () as e:  # TODO: add whitelisted exceptions
            raise e
        except Exception as e:
            msg = f"Repository {repo.name} failed with exception: {e!s}."
            if repo.issue_tracker is not None:
                msg += f"Please open an issue at {repo.issue_tracker}."
            get_logger().warning(msg)

    if data_repository is None:
        from urllib.parse import urlsplit  # pylint: disable=C0415

        repository = urlsplit(archive_url).netloc
        # TODO: refine error message
        raise ValueError(
            f"Invalid data repository '{repository}'. "
            "To request or contribute support for this repository, "
            "please open an issue at https://github.com/ssciwr/pooch-doi/issues"
        )

    if data_repository.user_warning is not None:
        get_logger().warning(
            f"Selected Repository {data_repository.name} issued a warning:"
            f"{data_repository.user_warning}"
        )

    return data_repository


class DataRepository:  # pylint: disable=too-few-public-methods, missing-class-docstring
    # TODO: add allowed_exceptions

    # A URL for an issue tracker for this implementation
    issue_tracker: Optional[str] = None

    # Whether the repository allows self-hosting
    allows_self_hosting: bool = False

    # Whether this repository is fully supported (meaning that all public data
    # from this repository is accessible via pooch).
    full_support: bool = True

    # A warning message to display to the end user if this repository is used.
    # This can be useful whenever a data repository is only partially supported.
    user_warning: Optional[str] = None

    # Whether this implementation performs requests to external services
    # during initialization. We use this to minimize the execution time.
    init_requires_requests: bool = True

    @property
    def name(self) -> str:
        """
        The display name of the repository.
        """
        raise NotImplementedError  # pragma: no cover

    @property
    def homepage(self) -> str:
        """
        The homepage URL of the repository.
        This could be the URL of the actual service or the URL of the project,
        if it is a data repository that allows self-hosting.
        """
        raise NotImplementedError  # pragma: no cover

    @classmethod
    def initialize(cls, doi, archive_url):  # pylint: disable=unused-argument
        """
        Initialize the data repository if the given URL points to a
        corresponding repository.

        Initializes a data repository object. This is done as part of
        a chain of responsibility. If the class cannot handle the given
        repository URL, it returns `None`. Otherwise a `DataRepository`
        instance is returned.

        Parameters
        ----------
        doi : str
            The DOI that identifies the repository
        archive_url : str
            The resolved URL for the DOI
        """

        return None  # pragma: no cover

    def download_url(self, file_name):
        """
        Use the repository API to get the download URL for a file given
        the archive URL.

        Parameters
        ----------
        file_name : str
            The name of the file in the archive that will be downloaded.

        Returns
        -------
        download_url : str
            The HTTP URL that can be used to download the file.
        """

        raise NotImplementedError  # pragma: no cover

    def create_registry(self) -> Dict[str, str]:
        """
        Create a registry dictionary using the data repository's API

        Returns
        ----------
        registry : Dict[str,str]
            The registry dictionary.
        """
        # TODO: maybe add some mechanism to cache registry
        raise NotImplementedError  # pragma: no cover
