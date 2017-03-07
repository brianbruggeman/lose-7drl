# -*- coding: utf-8 -*-
import pytest


@pytest.mark.unit
@pytest.mark.parametrize("width, height, title, fullscreen", [
    (None, None, None, None),
    (80, 50, 'Untitled', None),

])
def test_create_window(width, height, title, fullscreen, window):
    from lose.utils.ui.panels import Panel

    panel = Panel(width, height, title, fullscreen, parent=window)
    print(panel)
