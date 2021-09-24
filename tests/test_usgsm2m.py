"""Tests for usgsm2m module."""

import os
import pytest

from usgsm2m.usgsm2m import USGSM2M
from usgsm2m.errors import USGSM2MError


@pytest.fixture(scope="module")
def ee():
    return USGSM2M(
        os.getenv("USGSM2M_USERNAME"), os.getenv("USGSM2M_PASSWORD")
    )


def test_ee_login(ee):
    assert ee.logged_in()


def test_ee_login_error():
    with pytest.raises(USGSM2MError):
        USGSM2MError("bad_username", "bad_password")
