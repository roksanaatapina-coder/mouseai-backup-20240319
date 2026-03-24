#!/usr/bin/env python3
"""
MouseAI 2.0 - Лучшая программа для анализа игровой мыши в мире

Этот пакет содержит все модули MouseAI 2.0:
- Ядро системы (сбор данных, детекция игр)
- Научный анализ (метрики, ML, рекомендации)
- Визуализация (тепловые карты, графики)
- Интеграции (Discord, Telegram, OBS)
- UI (графический интерфейс)

MouseAI 2.0 использует передовые технологии машинного обучения
и научные методы анализа для улучшения игровых навыков.
"""

__version__ = "2.0.0"
__author__ = "MouseAI Team"
__description__ = "MouseAI 2.0 - Лучшая программа для анализа игровой мыши в мире"

# Импорты для удобства использования
from .core.data_collector import create_data_collector
from .core.game_detector import create_game_detector
from .analysis.scientific_metrics import create_scientific_metrics
from .analysis.ml_models import create_ml_models
from .visualization.heatmaps import create_heatmap_generator
from .integration.discord_bot import create_discord_bot
from .integration.telegram_bot import create_telegram_bot
from .ui.main_window import MouseAIMainWindow

# Экспорт основных классов
__all__ = [
    'create_data_collector',
    'create_game_detector', 
    'create_scientific_metrics',
    'create_ml_models',
    'create_heatmap_generator',
    'create_discord_bot',
    'create_telegram_bot',
    'MouseAIMainWindow'
]

def get_mouseai_info():
    """Получить информацию о MouseAI"""
    return {
        'version': __version__,
        'description': __description__,
        'author': __author__,
        'features': [
            'Автоматический сбор данных с мыши и клавиатуры',
            'Авто-детект игр (CS2, PUBG, Valorant, Apex и другие)',
            'Научные метрики из mousetrap и исследований',
            'Машинное обучение для анализа стиля игры',
            'Тепловые карты и 3D визуализация',
            'Интеграция с Discord и Telegram',
            'Мультиплатформенность (Windows, macOS, Linux)',
            'Полная автоматизация процессов'
        ],
        'supported_games': [
            'Counter-Strike 2',
            'PUBG: BATTLEGROUNDS', 
            'Valorant',
            'Apex Legends',
            'Overwatch 2',
            'Fortnite',
            'Rainbow Six Siege',
            'Call of Duty: Warzone',
            'Escape from Tarkov',
            'Rust'
        ]
    }

if __name__ == "__main__":
    info = get_mouseai_info()
    print(f"🎯 MouseAI {info['version']}")
    print(f"📝 {info['description']}")
    print(f"👤 {info['author']}")
    print("\n🚀 Возможности:")
    for feature in info['features']:
        print(f"   • {feature}")
    print("\n🎮 Поддерживаемые игры:")
    for game in info['supported_games']:
        print(f"   • {game}")
    print("\n🎯 MouseAI 2.0 - Реально помогает становиться лучше!")