#!/usr/bin/env python3
"""
MouseAILogger - Расширенный логгер для MouseAI
"""

import logging
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

class MouseAILogger:
    """Расширенный логгер для MouseAI"""
    
    def __init__(self, name: str = "MouseAI", log_level: str = "INFO"):
        """
        Инициализация логгера
        
        Args:
            name: Имя логгера
            log_level: Уровень логирования
        """
        self.name = name
        self.log_level = getattr(logging, log_level.upper(), logging.INFO)
        
        # Создаем директорию для логов
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)
        
        # Создаем имя файла лога с датой
        log_filename = f"mouseai_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        self.log_file = self.log_dir / log_filename
        
        # Настраиваем логгер
        self.logger = self._setup_logger()
        
    def _setup_logger(self) -> logging.Logger:
        """Настроить логгер"""
        logger = logging.getLogger(self.name)
        logger.setLevel(self.log_level)
        
        # Очищаем существующие обработчики
        logger.handlers.clear()
        
        # Формат сообщений
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Консольный обработчик
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.log_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # Файловый обработчик
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        file_handler.setLevel(self.log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        return logger
        
    def debug(self, message: str):
        """Логировать DEBUG сообщение"""
        self.logger.debug(message)
        
    def info(self, message: str):
        """Логировать INFO сообщение"""
        self.logger.info(message)
        
    def warning(self, message: str):
        """Логировать WARNING сообщение"""
        self.logger.warning(message)
        
    def error(self, message: str):
        """Логировать ERROR сообщение"""
        self.logger.error(message)
        
    def critical(self, message: str):
        """Логировать CRITICAL сообщение"""
        self.logger.critical(message)
        
    def exception(self, message: str):
        """Логировать исключение"""
        self.logger.exception(message)
        
    def set_level(self, level: str):
        """Установить уровень логирования"""
        self.log_level = getattr(logging, level.upper(), logging.INFO)
        self.logger.setLevel(self.log_level)
        
        # Обновляем уровень для всех обработчиков
        for handler in self.logger.handlers:
            handler.setLevel(self.log_level)
            
    def get_log_file(self) -> Path:
        """Получить путь к файлу лога"""
        return self.log_file
        
    def get_log_dir(self) -> Path:
        """Получить путь к директории логов"""
        return self.log_dir
        
    def cleanup_old_logs(self, days: int = 7):
        """
        Очистить старые логи
        
        Args:
            days: Количество дней хранения логов
        """
        cutoff_date = datetime.now().timestamp() - (days * 24 * 3600)
        
        for log_file in self.log_dir.glob("*.log"):
            if log_file.stat().st_mtime < cutoff_date:
                log_file.unlink()
                
    def get_latest_log_file(self) -> Optional[Path]:
        """Получить последний файл лога"""
        log_files = list(self.log_dir.glob("*.log"))
        if not log_files:
            return None
            
        return max(log_files, key=lambda f: f.stat().st_mtime)
        
    def read_log(self, lines: int = 100) -> str:
        """
        Прочитать последние строки из лога
        
        Args:
            lines: Количество строк для чтения
            
        Returns:
            Содержимое лога
        """
        if not self.log_file.exists():
            return "Файл лога не найден"
            
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                all_lines = f.readlines()
                return ''.join(all_lines[-lines:])
        except Exception as e:
            return f"Ошибка чтения лога: {e}"
            
    def clear_log(self):
        """Очистить текущий файл лога"""
        try:
            with open(self.log_file, 'w', encoding='utf-8') as f:
                f.write("")
        except Exception as e:
            self.error(f"Ошибка очистки лога: {e}")

# Глобальный экземпляр логгера
mouseai_logger = MouseAILogger()

def get_logger(name: str = "MouseAI") -> MouseAILogger:
    """Получить экземпляр логгера"""
    return MouseAILogger(name)

# Удобные функции для быстрого логирования
def debug(message: str):
    """Быстрое DEBUG логирование"""
    mouseai_logger.debug(message)
    
def info(message: str):
    """Быстрое INFO логирование"""
    mouseai_logger.info(message)
    
def warning(message: str):
    """Быстрое WARNING логирование"""
    mouseai_logger.warning(message)
    
def error(message: str):
    """Быстрое ERROR логирование"""
    mouseai_logger.error(message)
    
def critical(message: str):
    """Быстрое CRITICAL логирование"""
    mouseai_logger.critical(message)

if __name__ == "__main__":
    # Тестирование логгера
    logger = MouseAILogger("TestLogger", "DEBUG")
    
    logger.info("Тестирование логгера...")
    logger.debug("Это debug сообщение")
    logger.warning("Это warning сообщение")
    logger.error("Это error сообщение")
    
    print(f"Лог файл: {logger.get_log_file()}")
    print(f"Последние 10 строк лога:\n{logger.read_log(10)}")