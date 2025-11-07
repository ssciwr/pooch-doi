import pytest
from pooch_doi import utils

_VALID_DOIS = (
    "10.5281/zenodo.17544720",
    "10.6084/m9.figshare.30511304",
)
_INVALID_DOIS = (
    "11.5281/zenodo.17544720",
    "10.60/m9.figshare.30511304",
)


@pytest.mark.unit
def test_is_valid_doi():
    for doi in _VALID_DOIS:
        assert utils.is_valid_doi(doi) is True
    for doi in _INVALID_DOIS:
        assert utils.is_valid_doi(doi) is False


@pytest.mark.unit
def test_assert_valid_doi():
    for doi in _VALID_DOIS:
        utils.assert_valid_doi(doi)

@pytest.mark.unit
def test_assert_invalid_doi():
    for doi in _INVALID_DOIS:
        with pytest.raises(ValueError):
            utils.assert_valid_doi(doi)
