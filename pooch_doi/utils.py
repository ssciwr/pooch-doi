from typing import Tuple
import logging
import re


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
    # We will valid the dois by following the regular expression: /(10[.][0-9]{4,}[^\s"\/<>]*\/[^\s"<>]+)/
    # small interpretation for later adjustements:
    # 10[.][0-9]{4,} -> a "10" followed by "." followed by at least 4 Numbers between 0 and 9 
    # Example: 10.3456
    # [^\s"\/<>]* -> Match any character except of: “\s” -> all whitespace elements ,""" -> ",
    # "\/" -> /,"<“,">" zero or more times.
    # \/[^\s"<>]+ -> a "/" followed by any characters except of: “\s” -> all whitespace elements,
    # """ -> ", "<“, ">" one or more times.
    validdoi = doi
    validdoi = re.search("(10[.][0-9]{4,}[^\s\"\/<>]*\/[^\s\"<>]+)",doi)
    if validdoi is None:
        return False
    else:
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
