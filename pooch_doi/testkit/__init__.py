try:
    import pytest
except ImportError:
    raise ImportError(
        """
    Pytest is not installed. To use the provided pooch-doi testing utilities,
    please install pytest.
    """
    )

pytest.register_assert_rewrite("pooch_doi.testkit.repository")

from .repository import *
