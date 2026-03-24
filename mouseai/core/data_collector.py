#!/usr/bin/env python3
"""
DataCollector - Сбор данных с мыши, клавиатуры и системных метрик
"""

import time
import threading
import asyncio
import platform
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Deque
from dataclasses import dataclass, asdict
from collections import deque
from pathlib import Path
import logging

# Platform-specific imports
if platform.system() == "Windows":
    import win32api
    import win32con
    import win32gui
    import pywintypes
elif platform.system() == "Darwin":  # macOS
    import Quartz
    import AppKit
elif platform.system() == "Linux":
    import Xlib.display
    import Xlib.X
    import Xlib.XK
    import Xlib.protocol.event

logger = logging.getLogger(__name__)

class RingBuffer:
    """Кольцевой буфер для эффективного хранения данных"""
    
    def __init__(self, max_size: int = 10000):
        self.max_size = max_size
        self.buffer = deque(maxlen=max_size)
        self.total_items = 0
        
    def append(self, item):
        """Добавить элемент в буфер"""
        self.buffer.append(item)
        self.total_items += 1
        
    def get_all(self) -> List:
        """Получить все элементы"""
        return list(self.buffer)
        
    def clear(self):
        """Очистить буфер"""
        self.buffer.clear()
        self.total_items = 0
        
    def size(self) -> int:
        """Получить размер буфера"""
        return len(self.buffer)

class DataCollector:
    """Универсальный сборщик данных для всех платформ с асинхронной обработкой"""
    
    def __init__(self, buffer_size: int = 10000, sampling_rate: int = 100):
        self.platform = platform.system()
        self.is_recording = False
        self.sampling_rate = sampling_rate  # Hz
        self.buffer_size = buffer_size
        
        # Ring buffers для эффективного хранения данных
        self.mouse_buffer = RingBuffer(buffer_size)
        self.keyboard_buffer = RingBuffer(buffer_size // 10)  # Клавиатура реже
        self.system_buffer = RingBuffer(buffer_size // 20)    # Системные метрики реже
        
        # Platform-specific setup
        if self.platform == "Windows":
            self._setup_windows()
        elif self.platform == "Darwin":
            self._setup_macos()
        elif self.platform == "Linux":
            self._setup_linux()
            
        self.recording_thread = None
        self.stop_event = threading.Event()
        self._last_position = None
        self._last_speed = 0.0
        self._system_update_interval = 0.5
        self._last_system_update = 0
        
        # Статистика производительности
        self._stats = {
            'total_samples': 0,
            'dropped_samples': 0,
            'processing_time': 0.0
        }
        
    def _setup_windows(self):
        """Настройка Windows сборщика с обработкой ошибок"""
        try:
            self.mouse_hook = None
            self.keyboard_hook = None
            logger.info("Windows platform setup completed")
        except Exception as e:
            logger.error(f"Windows setup failed: {e}")
            raise
            
    def _setup_macos(self):
        """Настройка macOS сборщика с проверкой привилегий"""
        try:
            # Проверка доступа к событиям мыши
            self.event_tap = None
            logger.info("macOS platform setup completed")
        except Exception as e:
            logger.error(f"macOS setup failed: {e}")
            raise
            
    def _setup_linux(self):
        """Настройка Linux сборщика с обработкой дисплея"""
        try:
            self.display = Xlib.display.Display()
            self.root = self.display.screen().root
            logger.info("Linux platform setup completed")
        except Exception as e:
            logger.error(f"Linux setup failed: {e}")
            raise
        
    def start_recording(self):
        """Начать запись данных"""
        if self.is_recording:
            return
            
        self.is_recording = True
        self.stop_event.clear()
        self.mouse_data = []
        self.keyboard_data = []
        self.system_data = []
        
        # Запускаем запись в отдельном потоке
        self.recording_thread = threading.Thread(target=self._record_loop)
        self.recording_thread.daemon = True
        self.recording_thread.start()
        
        print(f"📹 Начата запись данных ({self.platform})")
        
    def stop_recording(self) -> Dict:
        """Остановить запись и вернуть собранные данные"""
        if not self.is_recording:
            return {}
            
        self.is_recording = False
        self.stop_event.set()
        
        if self.recording_thread:
            self.recording_thread.join(timeout=2.0)
            
        # Собираем все данные из ring buffers
        session_data = {
            "platform": self.platform,
            "start_time": datetime.now().isoformat(),
            "mouse_data": self.mouse_buffer.get_all(),
            "keyboard_data": self.keyboard_buffer.get_all(),
            "system_data": self.system_buffer.get_all(),
            "session_duration": len(self.mouse_buffer.get_all()) / self.sampling_rate,
            "performance_stats": self._stats.copy()
        }
        
        # Логируем статистику производительности
        total_time = self._stats['processing_time']
        total_samples = self._stats['total_samples']
        dropped_samples = self._stats['dropped_samples']
        
        if total_samples > 0:
            avg_processing_time = total_time / total_samples
            drop_rate = (dropped_samples / total_samples) * 100
            
            logger.info(f"📊 Сессия завершена:")
            logger.info(f"   - Собранные данные: {len(session_data['mouse_data'])} mouse, {len(session_data['keyboard_data'])} keyboard")
            logger.info(f"   - Производительность: {avg_processing_time*1000:.2f}ms/сэмпл")
            logger.info(f"   - Потеряно сэмплов: {drop_rate:.1f}%")
        
        return session_data
        
    def _record_loop(self):
        """Основной цикл записи с оптимизацией производительности"""
        last_system_update = time.time()
        last_mouse_update = time.time()
        mouse_interval = 1.0 / self.sampling_rate  # Интервал между измерениями
        
        while not self.stop_event.is_set():
            current_time = time.time()
            processing_start = time.time()
            
            # Сбор системных метрик (реже)
            if current_time - last_system_update > self._system_update_interval:
                self._collect_system_metrics()
                last_system_update = current_time
            
            # Сбор данных о мыши с адаптивной частотой
            if current_time - last_mouse_update >= mouse_interval:
                mouse_pos = self._get_mouse_position()
                if mouse_pos:
                    # Используем ring buffer вместо списка
                    self.mouse_buffer.append({
                        "timestamp": current_time,
                        "x": mouse_pos[0],
                        "y": mouse_pos[1],
                        "window": self._get_active_window()
                    })
                    self._stats['total_samples'] += 1
                last_mouse_update = current_time
            
            # Оптимизация: динамическое управление частотой
            processing_time = time.time() - processing_start
            self._stats['processing_time'] += processing_time
            
            # Адаптивная задержка для поддержания стабильной частоты
            sleep_time = max(0, mouse_interval - processing_time)
            if sleep_time > 0:
                time.sleep(sleep_time)
            else:
                self._stats['dropped_samples'] += 1
            
    def _get_mouse_position(self) -> Optional[Tuple[int, int]]:
        """Получить текущую позицию мыши с валидацией"""
        try:
            if self.platform == "Windows":
                pos = win32api.GetCursorPos()
                # Валидация координат для Windows
                if pos and len(pos) == 2 and all(isinstance(x, int) for x in pos):
                    return pos
            elif self.platform == "Darwin":
                loc = Quartz.NSEvent.mouseLocation()
                pos = (int(loc.x), int(loc.y))
                # Валидация координат для macOS
                if pos and all(isinstance(x, int) for x in pos):
                    return pos
            elif self.platform == "Linux":
                data = self.root.query_pointer()
                pos = (data.root_x, data.root_y)
                # Валидация координат для Linux
                if pos and all(isinstance(x, int) for x in pos):
                    return pos
        except Exception as e:
            logger.error(f"Ошибка получения позиции мыши: {e}")
            return None
            
    def _get_active_window(self) -> str:
        """Получить активное окно"""
        try:
            if self.platform == "Windows":
                hwnd = win32gui.GetForegroundWindow()
                return win32gui.GetWindowText(hwnd)
            elif self.platform == "Darwin":
                active_app = AppKit.NSWorkspace.sharedWorkspace().activeApplication()
                return active_app['NSApplicationName']
            elif self.platform == "Linux":
                # Простая реализация для Linux
                return "Linux Window"
        except Exception:
            return "Unknown"
            
    def _collect_system_metrics(self):
        """Сбор системных метрик"""
        try:
            import psutil
            
            metrics = {
                "timestamp": time.time(),
                "cpu_percent": psutil.cpu_percent(interval=0.1),
                "memory_percent": psutil.virtual_memory().percent,
                "active_window": self._get_active_window(),
                "system_time": datetime.now().isoformat()
            }
            
            self.system_data.append(metrics)
            
        except ImportError:
            # Если psutil не установлен
            self.system_data.append({
                "timestamp": time.time(),
                "cpu_percent": 0,
                "memory_percent": 0,
                "active_window": self._get_active_window(),
                "system_time": datetime.now().isoformat()
            })

@dataclass
class MouseMovement:
    """Данные о движении мыши"""
    timestamp: float
    x: int
    y: int
    dx: float = 0.0
    dy: float = 0.0
    speed: float = 0.0
    acceleration: float = 0.0

@dataclass
class KeyboardEvent:
    """Данные о нажатии клавиши"""
    timestamp: float
    key: str
    action: str  # 'press' or 'release'
    modifiers: List[str]

class AdvancedDataCollector(DataCollector):
    """Расширенный сборщик с анализом движений"""
    
    def __init__(self):
        super().__init__()
        self.last_position = None
        self.last_speed = 0.0
        self.movement_buffer = []
        
    def _record_loop(self):
        """Расширенный цикл записи с анализом движений"""
        last_system_update = time.time()
        
        while not self.stop_event.is_set():
            current_time = time.time()
            
            # Сбор системных метрик
            if current_time - last_system_update > 0.5:
                self._collect_system_metrics()
                last_system_update = current_time
                
            # Сбор данных о мыши с анализом
            mouse_pos = self._get_mouse_position()
            if mouse_pos:
                movement = self._analyze_movement(current_time, mouse_pos)
                if movement:
                    self.mouse_data.append(movement)
                    
            time.sleep(0.01)  # 100Hz
            
    def _analyze_movement(self, timestamp: float, pos: Tuple[int, int]) -> Optional[MouseMovement]:
        """Анализ движения мыши"""
        if self.last_position is None:
            self.last_position = pos
            return None
            
        # Расчет дельт
        dx = pos[0] - self.last_position[0]
        dy = pos[1] - self.last_position[1]
        distance = (dx**2 + dy**2)**0.5
        
        # Расчет скорости (пиксели в секунду)
        dt = 0.01  # 100Hz
        speed = distance / dt if distance > 0 else 0
        
        # Расчет ускорения
        acceleration = (speed - self.last_speed) / dt if self.last_speed > 0 else 0
        
        # Сохраняем для следующей итерации
        self.last_position = pos
        self.last_speed = speed
        
        # Фильтрация слишком маленьких движений
        if distance < 0.1:
            return None
            
        return MouseMovement(
            timestamp=timestamp,
            x=pos[0],
            y=pos[1],
            dx=dx,
            dy=dy,
            speed=speed,
            acceleration=acceleration
        )

def create_data_collector():
    """Фабрика для создания сборщика данных"""
    return AdvancedDataCollector()

# Пример использования
if __name__ == "__main__":
    collector = create_data_collector()
    
    print("📹 Тестирование DataCollector...")
    print(f"Платформа: {collector.platform}")
    
    # Тест записи 5 секунд
    collector.start_recording()
    time.sleep(5)
    data = collector.stop_recording()
    
    print(f"📊 Собрано данных:")
    print(f"   - Mouse movements: {len(data.get('mouse_data', []))}")
    print(f"   - System metrics: {len(data.get('system_data', []))}")
    print(f"   - Platform: {data.get('platform', 'Unknown')}")
    
    # Анализ первых 10 движений
    if 'mouse_data' in data and data['mouse_data']:
        print("\n📈 Первые 10 движений:")
        for i, movement in enumerate(data['mouse_data'][:10]):
            if hasattr(movement, 'speed'):
                print(f"   {i+1}. Speed: {movement.speed:.2f} px/s, Acc: {movement.acceleration:.2f} px/s²")
            else:
                print(f"   {i+1}. Basic movement data")