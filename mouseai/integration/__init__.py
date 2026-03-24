#!/usr/bin/env python3
"""
MouseAI Integration - Интеграции с внешними сервисами
"""

from .discord_bot import create_discord_bot
from .telegram_bot import create_telegram_bot
from .obs_overlay import create_obs_overlay
from .rest_api import create_rest_api

__all__ = [
    'create_discord_bot',
    'create_telegram_bot',
    'create_obs_overlay',
    'create_rest_api'
]