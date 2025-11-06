from typing import Tuple
import logging


LOGGER = logging.Logger("pooch-doi")
LOGGER.addHandler(logging.StreamHandler())


def get_logger() -> logging.Logger:
    r"""
    Get the default event logger.

    The logger records events like downloading files, unzipping archives, etc.
    Use the method :meth:`logging.Logger.setLevel` of this object to adjust the
    verbosity level from Pooch.

    Returns
    -------
    logger : :class:`logging.Logger`
        The logger object for Pooch
    """
    return LOGGER


def is_valid_doi(doi: str) -> bool:
    # TODO: implement this validation logic
    return True


def assert_valid_doi(doi: str):
    if not is_valid_doi(doi):
        raise ValueError(f"Invalid DOI: {doi!s}")


def parse_doi(doi: str) -> Tuple[str, str]:
    if doi.startswith("doi://"):
        raise ValueError(
            f"Invalid DOI link '{doi}'. You must not use '//' after 'doi:'."
        )
    if doi.startswith("doi:"):
        doi = doi[4:]
    parts = doi.split("/")
    if "zenodo" in parts[1].lower():
        netloc = "/".join(parts[:2])
        path = "/" + "/".join(parts[2:])
    else:
        netloc = "/".join(parts[:-1])
        path = "/" + parts[-1]
    return netloc, path
