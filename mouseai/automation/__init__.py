#!/usr/bin/env python3
"""
MouseAI Automation - Автоматизация процессов
"""

from .auto_session import create_auto_session_manager
from .auto_analyzer import create_auto_analyzer
from .auto_updater import create_auto_updater

__all__ = [
    'create_auto_session_manager',
    'create_auto_analyzer',
    'create_auto_updater'
]