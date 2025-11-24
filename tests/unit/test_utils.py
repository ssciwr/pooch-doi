import pytest
from pooch_doi import utils


@pytest.mark.unit
def test_is_valid_doi(dois):
    for doi in dois.all_valid_dois():
        assert utils.is_valid_doi(doi) is True


@pytest.mark.unit
def test_is_invalid_doi(dois):
    for doi in dois.all_invalid_dois():
        assert utils.is_valid_doi(doi) is False


@pytest.mark.unit
def test_assert_valid_doi(dois):
    for doi in dois.all_valid_dois():
        utils.assert_valid_doi(doi)


@pytest.mark.unit
def test_assert_invalid_doi(dois):
    for doi in dois.all_invalid_dois():
        with pytest.raises(ValueError):
            utils.assert_valid_doi(doi)
