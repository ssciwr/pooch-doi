import pooch

import pooch_doi


def test_pooch_doi():
    _ = pooch_doi.DOIPooch(
        path=pooch.os_cache("poch_doi_test"),
        doi="10.5281/zenodo.4924875",
        populate_registry=False,
    )
