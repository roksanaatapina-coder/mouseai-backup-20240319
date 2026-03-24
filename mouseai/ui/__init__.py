#!/usr/bin/env python3
"""
MouseAI UI - Графический интерфейс
"""

from .main_window import MouseAIMainWindow
from .game_selection import create_game_selector
from .dashboard import create_analysis_dashboard
from .settings import create_settings_window

__all__ = [
    'MouseAIMainWindow',
    'create_game_selector',
    'create_analysis_dashboard',
    'create_settings_window'
]