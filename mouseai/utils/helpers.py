#!/usr/bin/env python3
"""
MouseAI Helpers - Вспомогательные функции и утилиты
"""

import os
import sys
import json
import logging
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
import numpy as np
from pathlib import Path

class MouseAIHelpers:
    """Класс вспомогательных функций"""
    
    @staticmethod
    def validate_mouse_data(data: Dict) -> bool:
        """Проверить валидность данных о мыши"""
        required_fields = ['x', 'y', 'timestamp']
        
        if not isinstance(data, dict):
            return False
            
        for field in required_fields:
            if field not in data:
                return False
                
        # Проверяем типы данных
        if not isinstance(data['x'], (int, float)) or not isinstance(data['y'], (int, float)):
            return False
            
        if not isinstance(data['timestamp'], (int, float)):
            return False
            
        return True
        
    @staticmethod
    def calculate_distance(point1: tuple, point2: tuple) -> float:
        """Рассчитать расстояние между двумя точками"""
        return ((point2[0] - point1[0])**2 + (point2[1] - point1[1])**2)**0.5
        
    @staticmethod
    def calculate_velocity(distance: float, time_delta: float) -> float:
        """Рассчитать скорость"""
        if time_delta <= 0:
            return 0.0
        return distance / time_delta
        
    @staticmethod
    def calculate_acceleration(velocity1: float, velocity2: float, time_delta: float) -> float:
        """Рассчитать ускорение"""
        if time_delta <= 0:
            return 0.0
        return (velocity2 - velocity1) / time_delta
        
    @staticmethod
    def smooth_data(data: List[float], window_size: int = 3) -> List[float]:
        """Сгладить данные с помощью скользящего среднего"""
        if len(data) < window_size:
            return data
            
        smoothed = []
        for i in range(len(data)):
            start = max(0, i - window_size // 2)
            end = min(len(data), i + window_size // 2 + 1)
            window = data[start:end]
            smoothed.append(sum(window) / len(window))
            
        return smoothed
        
    @staticmethod
    def detect_peaks(data: List[float], threshold: float = 0.5) -> List[int]:
        """Найти пики в данных"""
        peaks = []
        for i in range(1, len(data) - 1):
            if data[i] > data[i-1] and data[i] > data[i+1] and data[i] > threshold:
                peaks.append(i)
        return peaks
        
    @staticmethod
    def normalize_data(data: List[float]) -> List[float]:
        """Нормализовать данные в диапазон [0, 1]"""
        if not data:
            return []
            
        min_val = min(data)
        max_val = max(data)
        range_val = max_val - min_val
        
        if range_val == 0:
            return [0.5] * len(data)
            
        return [(x - min_val) / range_val for x in data]
        
    @staticmethod
    def calculate_statistics(data: List[float]) -> Dict[str, float]:
        """Рассчитать статистику по данным"""
        if not data:
            return {}
            
        return {
            'mean': np.mean(data),
            'std': np.std(data),
            'min': np.min(data),
            'max': np.max(data),
            'median': np.median(data),
            'q25': np.percentile(data, 25),
            'q75': np.percentile(data, 75)
        }
        
    @staticmethod
    def format_time(seconds: float) -> str:
        """Форматировать время в читаемый вид"""
        if seconds < 60:
            return f"{seconds:.1f} сек"
        elif seconds < 3600:
            minutes = seconds // 60
            seconds = seconds % 60
            return f"{minutes:.0f} мин {seconds:.0f} сек"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            seconds = seconds % 60
            return f"{hours:.0f} ч {minutes:.0f} мин {seconds:.0f} сек"
            
    @staticmethod
    def get_game_from_process(process_name: str) -> str:
        """Определить игру по названию процесса"""
        game_mapping = {
            'cs2.exe': 'CS2',
            'pubg.exe': 'PUBG',
            'valorant.exe': 'Valorant',
            'overwatch.exe': 'Overwatch',
            'r6.exe': 'Rainbow Six Siege',
            'cod.exe': 'Call of Duty: Warzone',
            'fortnite.exe': 'Fortnite',
            'apex.exe': 'Apex Legends',
            'tarkov.exe': 'Escape from Tarkov'
        }
        
        return game_mapping.get(process_name.lower(), 'Unknown')
        
    @staticmethod
    def create_directory_if_not_exists(path: str):
        """Создать директорию, если она не существует"""
        Path(path).mkdir(parents=True, exist_ok=True)
        
    @staticmethod
    def save_json(data: Dict, filename: str, indent: int = 2):
        """Сохранить данные в JSON файл"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=indent, ensure_ascii=False)
            return True
        except Exception as e:
            logging.error(f"Ошибка сохранения JSON: {e}")
            return False
            
    @staticmethod
    def load_json(filename: str) -> Optional[Dict]:
        """Загрузить данные из JSON файла"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Ошибка загрузки JSON: {e}")
            return None
            
    @staticmethod
    def get_timestamp() -> str:
        """Получить текущую метку времени"""
        return datetime.now().isoformat()
        
    @staticmethod
    def get_date_string() -> str:
        """Получить строку с датой"""
        return datetime.now().strftime('%Y-%m-%d')
        
    @staticmethod
    def get_time_string() -> str:
        """Получить строку с временем"""
        return datetime.now().strftime('%H:%M:%S')
        
    @staticmethod
    def is_weekend() -> bool:
        """Проверить, является ли сегодня выходным"""
        return datetime.now().weekday() >= 5
        
    @staticmethod
    def get_weekday() -> str:
        """Получить название дня недели"""
        weekdays = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
        return weekdays[datetime.now().weekday()]
        
    @staticmethod
    def calculate_session_duration(start_time: datetime, end_time: datetime) -> float:
        """Рассчитать длительность сессии в секундах"""
        return (end_time - start_time).total_seconds()
        
    @staticmethod
    def format_bytes(bytes_size: int) -> str:
        """Форматировать размер в байтах"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.1f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.1f} TB"
        
    @staticmethod
    def get_system_info() -> Dict[str, Any]:
        """Получить информацию о системе"""
        import platform
        import psutil
        
        return {
            'platform': platform.platform(),
            'system': platform.system(),
            'processor': platform.processor(),
            'architecture': platform.architecture(),
            'python_version': platform.python_version(),
            'cpu_count': psutil.cpu_count(),
            'memory_total': psutil.virtual_memory().total,
            'memory_available': psutil.virtual_memory().available,
            'disk_usage': psutil.disk_usage('/').total if os.name != 'nt' else psutil.disk_usage('C:').total
        }
        
    @staticmethod
    def validate_email(email: str) -> bool:
        """Проверить валидность email"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
        
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Очистить имя файла от недопустимых символов"""
        import re
        # Заменяем недопустимые символы на подчеркивания
        return re.sub(r'[<>:"/\\|?*]', '_', filename)
        
    @staticmethod
    def generate_unique_id() -> str:
        """Сгенерировать уникальный идентификатор"""
        import uuid
        return str(uuid.uuid4())
        
    @staticmethod
    def clamp(value: float, min_val: float, max_val: float) -> float:
        """Ограничить значение в заданном диапазоне"""
        return max(min_val, min(max_val, value))
        
    @staticmethod
    def interpolate(start: float, end: float, factor: float) -> float:
        """Линейная интерполяция между двумя значениями"""
        return start + (end - start) * factor
        
    @staticmethod
    def exponential_moving_average(data: List[float], alpha: float = 0.3) -> List[float]:
        """Рассчитать экспоненциальную скользящую среднюю"""
        if not data:
            return []
            
        ema = [data[0]]
        for i in range(1, len(data)):
            ema.append(alpha * data[i] + (1 - alpha) * ema[-1])
            
        return ema
        
    @staticmethod
    def detect_outliers(data: List[float], threshold: float = 2.0) -> List[int]:
        """Найти выбросы в данных"""
        if len(data) < 3:
            return []
            
        mean = np.mean(data)
        std = np.std(data)
        
        outliers = []
        for i, value in enumerate(data):
            if abs(value - mean) > threshold * std:
                outliers.append(i)
                
        return outliers
        
    @staticmethod
    def calculate_correlation(x: List[float], y: List[float]) -> float:
        """Рассчитать коэффициент корреляции"""
        if len(x) != len(y) or len(x) < 2:
            return 0.0
            
        return np.corrcoef(x, y)[0, 1]
        
    @staticmethod
    def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
        """Безопасное деление с обработкой деления на ноль"""
        try:
            if denominator == 0:
                return default
            return numerator / denominator
        except:
            return default
            
    @staticmethod
    def format_number(number: float, decimals: int = 2) -> str:
        """Форматировать число с заданным количеством знаков после запятой"""
        return f"{number:.{decimals}f}"
        
    @staticmethod
    def get_memory_usage() -> Dict[str, float]:
        """Получить информацию об использовании памяти"""
        import psutil
        
        memory = psutil.virtual_memory()
        return {
            'total': memory.total,
            'available': memory.available,
            'used': memory.used,
            'percentage': memory.percent,
            'free': memory.free
        }
        
    @staticmethod
    def get_cpu_usage(interval: float = 1.0) -> float:
        """Получить загрузку CPU"""
        return psutil.cpu_percent(interval=interval)
        
    @staticmethod
    def run_in_thread(func: Callable, *args, **kwargs):
        """Запустить функцию в отдельном потоке"""
        thread = threading.Thread(target=func, args=args, kwargs=kwargs, daemon=True)
        thread.start()
        return thread
        
    @staticmethod
    def debounce(wait_time: float):
        """Декоратор для debounce"""
        def decorator(func):
            def debounced(*args, **kwargs):
                def call_it():
                    func(*args, **kwargs)
                    
                if hasattr(debounced, '_timer'):
                    debounced._timer.cancel()
                    
                debounced._timer = threading.Timer(wait_time, call_it)
                debounced._timer.start()
                
            debounced._timer = None
            return debounced
        return decorator
        
    @staticmethod
    def throttle(wait_time: float):
        """Декоратор для throttle"""
        def decorator(func):
            last_called = [0.0]
            
            def throttled(*args, **kwargs):
                elapsed = time.time() - last_called[0]
                if elapsed > wait_time:
                    last_called[0] = time.time()
                    return func(*args, **kwargs)
                    
            return throttled
        return decorator

class PerformanceTimer:
    """Таймер для измерения производительности"""
    
    def __init__(self, name: str = "Operation"):
        self.name = name
        self.start_time = None
        self.end_time = None
        
    def __enter__(self):
        self.start_time = time.time()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        duration = self.end_time - self.start_time
        logging.info(f"{self.name} completed in {duration:.4f} seconds")
        
    def get_duration(self) -> float:
        """Получить длительность операции"""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0.0

class RateLimiter:
    """Ограничитель частоты вызовов"""
    
    def __init__(self, max_calls: int, time_window: float):
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = []
        self.lock = threading.Lock()
        
    def acquire(self) -> bool:
        """Попытаться получить разрешение на вызов"""
        with self.lock:
            now = time.time()
            
            # Удаляем старые вызовы
            self.calls = [call_time for call_time in self.calls if now - call_time < self.time_window]
            
            # Проверяем лимит
            if len(self.calls) < self.max_calls:
                self.calls.append(now)
                return True
                
            return False
            
    def wait(self):
        """Дождаться разрешения на вызов"""
        while not self.acquire():
            time.sleep(0.1)

def create_helpers() -> MouseAIHelpers:
    """Создать экземпляр вспомогательных функций"""
    return MouseAIHelpers()