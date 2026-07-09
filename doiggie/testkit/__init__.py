try:
    import pytest
except ImportError:
    raise ImportError(
        """
    Pytest is not installed. To use the provided doiggie testing utilities,
    please install pytest.
    """
    )

pytest.register_assert_rewrite("doiggie.testkit.repository")

from .repository import *
