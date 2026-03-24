#!/usr/bin/env python3
"""
MouseAI Main Entry Point
"""

import sys
import os
import argparse
from pathlib import Path

# Добавляем путь к проекту
sys.path.insert(0, str(Path(__file__).parent.parent))

from mouseai.core import MouseAI
from mouseai.ui import MouseAIMainWindow
from mouseai.utils import MouseAILogger
from mouseai.testing import MouseAITestBot

def main():
    """Главная функция запуска MouseAI"""
    
    parser = argparse.ArgumentParser(description='MouseAI - Advanced Mouse Movement Analysis')
    parser.add_argument('--mode', choices=['gui', 'cli', 'test', 'benchmark'], 
                       default='gui', help='Режим работы')
    parser.add_argument('--game', type=str, help='Игра для анализа')
    parser.add_argument('--duration', type=int, default=60, help='Длительность сессии в секундах')
    parser.add_argument('--test-mode', choices=['basic', 'advanced', 'all'], 
                       default='basic', help='Режим тестирования')
    
    args = parser.parse_args()
    
    # Инициализация логгера
    logger = MouseAILogger()
    logger.info("🚀 Запуск MouseAI...")
    
    try:
        if args.mode == 'gui':
            # Запуск GUI
            logger.info("🖥️  Запуск графического интерфейса...")
            app = MouseAIMainWindow()
            app.run()
            
        elif args.mode == 'cli':
            # Запуск CLI
            logger.info("💻 Запуск CLI режима...")
            mouseai = MouseAI()
            
            if args.game:
                logger.info(f"🎯 Анализ игры: {args.game}")
                mouseai.start_session(args.game, args.duration)
            else:
                logger.info("🎮 Доступные игры:")
                games = mouseai.get_supported_games()
                for game in games:
                    print(f"   - {game}")
                    
        elif args.mode == 'test':
            # Запуск тестов
            logger.info("🧪 Запуск тестирования...")
            test_bot = MouseAITestBot()
            
            if args.test_mode == 'basic':
                test_bot.run_basic_tests()
            elif args.test_mode == 'advanced':
                test_bot.run_advanced_tests()
            elif args.test_mode == 'all':
                test_bot.run_all_tests()
                
        elif args.mode == 'benchmark':
            # Запуск бенчмарка
            logger.info("⚡ Запуск бенчмарка...")
            test_bot = MouseAITestBot()
            test_bot.run_performance_benchmark()
            
    except KeyboardInterrupt:
        logger.info("🛑 Остановка MouseAI...")
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()