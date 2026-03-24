#!/usr/bin/env python3
"""
MouseAI Core - Основные компоненты системы
"""

# from .mouseai import MouseAI
from .data_collector import create_data_collector
from .game_detector import create_game_detector

__all__ = [
    'create_data_collector',
    'create_game_detector'
]
