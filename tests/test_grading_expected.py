"""Every scenario must ship reference data so `aste586 grade` works without
the hidden backend, and that data must be in sync with the reference."""

import pytest

from aste586.grading import expected_path, load_expected
from aste586.io import list_configs


@pytest.mark.parametrize("name", list_configs())
def test_expected_data_ships_for_every_scenario(name):
    assert expected_path(name).is_file(), (
        f"grading/expected/{name}.npz missing -- run `python tools/make_expected.py`")
    a = load_expected(name)
    assert "time" in a and a.meta["scenario"] == name


def test_expected_data_matches_reference_code():
    ref = pytest.importorskip("aste586_reference")
    from aste586.sim import backend_hash
    stale = [n for n in list_configs()
             if load_expected(n).meta["backend_hash"] != backend_hash(ref)]
    assert not stale, (
        f"expected data was generated from older reference code: {stale}; "
        "run `python tools/make_expected.py`")
