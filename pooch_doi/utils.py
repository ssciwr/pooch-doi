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


_DOI_REGEX_PATTERN = re.compile(r"(10[.][0-9]{2,}(?:[.][0-9]+)*/.+)")


def is_valid_doi(doi: str) -> bool:
    # we get the doi prefix from here: https://github.com/regexhq/doi-regex/
    # we only check the prefix, because the convention isn't very clear on that
    return _DOI_REGEX_PATTERN.match(doi) is not None


def assert_valid_doi(doi: str):
    if not is_valid_doi(doi):
        raise ValueError(f"Invalid DOI: {doi!s}")
