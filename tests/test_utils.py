# -*- coding: utf-8 -*-
import pytest


@pytest.mark.unit
@pytest.mark.parametrize("width, height", [
    (640, 480),
])
def test_create_window(width, height):
    from lose.utils import create_windows

    windows = create_windows(width, height)
    for name, window in windows.items():
        assert name is not None
        if name is not 'root':
            assert window is not None
        else:
            assert window is None
