#!/usr/bin/env python3
"""
GameDetector - Unified game detection system
Combines the best features from both versions with enhanced functionality
"""

import time
import psutil
import threading
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import re
import platform

# Import platform-specific modules
if platform.system() == "Windows":
    try:
        import win32gui
        import win32process
        WINDOWS_AVAILABLE = True
    except ImportError:
        WINDOWS_AVAILABLE = False
elif platform.system() == "Darwin":  # macOS
    try:
        import Quartz
        import AppKit
        MACOS_AVAILABLE = True
    except ImportError:
        print("Quartz недоступен. Установите pyobjc-framework-Quartz для macOS")
        MACOS_AVAILABLE = False
elif platform.system() == "Linux":
    try:
        import Xlib.display
        LINUX_AVAILABLE = True
    except ImportError:
        LINUX_AVAILABLE = False

@dataclass
class GameInfo:
    """Информация об игре"""
    name: str
    process_name: str
    window_title: str
    confidence: float
    pid: int
    start_time: float

class GameDetector:
    """Unified GameDetector with enhanced detection capabilities"""
    
    def __init__(self):
        self.platform = platform.system()
        self.is_monitoring = False
        self.monitoring_thread = None
        self.stop_event = threading.Event()
        
        # Поддерживаемые игры с улучшенными детекторами
        self.supported_games = {
            # FPS игры
            "CS2": {
                "process_names": ["cs2.exe", "cs2"],
                "window_titles": ["Counter-Strike 2", "Counter Strike 2"],
                "confidence": 0.95,
                "game_type": "fps",
                "category": "tactical_fps"
            },
            "PUBG": {
                "process_names": ["TslGame.exe", "PUBG.exe", "TslGame"],
                "window_titles": ["PUBG", "PLAYERUNKNOWN'S BATTLEGROUNDS"],
                "confidence": 0.90,
                "game_type": "fps",
                "category": "battle_royale"
            },
            "Valorant": {
                "process_names": ["VALORANT-Win64-Shipping.exe", "VALORANT"],
                "window_titles": ["VALORANT"],
                "confidence": 0.95,
                "game_type": "fps",
                "category": "hero_fps"
            },
            "Apex Legends": {
                "process_names": ["r5apex.exe", "Apex"],
                "window_titles": ["Apex Legends"],
                "confidence": 0.90,
                "game_type": "fps",
                "category": "battle_royale"
            },
            "Overwatch 2": {
                "process_names": ["Overwatch.exe", "Overwatch"],
                "window_titles": ["Overwatch 2", "Overwatch"],
                "confidence": 0.90,
                "game_type": "fps",
                "category": "hero_fps"
            },
            "Fortnite": {
                "process_names": ["FortniteClient-Win64-Shipping.exe", "Fortnite"],
                "window_titles": ["Fortnite"],
                "confidence": 0.85,
                "game_type": "fps",
                "category": "battle_royale"
            },
            "Rainbow Six Siege": {
                "process_names": ["RainbowSix.exe", "R6"],
                "window_titles": ["Rainbow Six Siege", "R6S"],
                "confidence": 0.90,
                "game_type": "fps",
                "category": "tactical_fps"
            },
            "Call of Duty: Warzone": {
                "process_names": ["cod.exe", "Warzone"],
                "window_titles": ["Call of Duty: Warzone", "Warzone"],
                "confidence": 0.85,
                "game_type": "fps",
                "category": "battle_royale"
            },
            "Escape from Tarkov": {
                "process_names": ["EscapeFromTarkov.exe", "Tarkov"],
                "window_titles": ["Escape from Tarkov", "Tarkov"],
                "confidence": 0.90,
                "game_type": "fps",
                "category": "survival"
            },
            "Rust": {
                "process_names": ["RustClient.exe", "Rust"],
                "window_titles": ["Rust"],
                "confidence": 0.85,
                "game_type": "fps",
                "category": "survival"
            },
            # RPG игры
            "Elden Ring": {
                "process_names": ["ELDENRING.exe", "EldenRing"],
                "window_titles": ["ELDEN RING", "Elden Ring"],
                "confidence": 0.90,
                "game_type": "rpg",
                "category": "action_rpg"
            },
            "The Witcher 3": {
                "process_names": ["witcher3.exe", "witcher3"],
                "window_titles": ["The Witcher 3", "Witcher 3"],
                "confidence": 0.90,
                "game_type": "rpg",
                "category": "action_rpg"
            },
            # Стратегии
            "StarCraft II": {
                "process_names": ["StarCraft II.exe", "SC2"],
                "window_titles": ["StarCraft II", "SC2"],
                "confidence": 0.95,
                "game_type": "strategy",
                "category": "rts"
            },
            "Age of Empires IV": {
                "process_names": ["AoE4.exe", "Age4"],
                "window_titles": ["Age of Empires IV", "AoE4"],
                "confidence": 0.90,
                "game_type": "strategy",
                "category": "rts"
            }
        }
        
        # Текущая активная игра
        self.current_game = None
        self.last_check_time = 0
        self.check_interval = 1.0  # Проверять каждую секунду
        
        # Статистика обнаружения
        self.detection_stats = {
            "total_checks": 0,
            "games_detected": 0,
            "false_positives": 0,
            "detection_rate": 0.0
        }
        
    def get_supported_games(self) -> List[str]:
        """Получить список поддерживаемых игр"""
        return list(self.supported_games.keys())
        
    def is_game_supported(self, game_name: str) -> bool:
        """Проверить, поддерживается ли игра"""
        return game_name in self.supported_games
        
    def detect_current_game(self) -> Optional[GameInfo]:
        """Обнаружить текущую активную игру"""
        try:
            self.detection_stats["total_checks"] += 1
            
            # Получаем активное окно
            active_window = self._get_active_window()
            if not active_window:
                return None
                
            # Проверяем все запущенные процессы
            for proc in psutil.process_iter(['pid', 'name', 'create_time']):
                try:
                    process_info = proc.info
                    process_name = process_info['name'].lower()
                    pid = process_info['pid']
                    
                    # Проверяем, является ли процесс игрой
                    game_info = self._check_process_for_game(process_name, active_window, pid)
                    if game_info:
                        self.detection_stats["games_detected"] += 1
                        return game_info
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
                    
            return None
            
        except Exception as e:
            print(f"Ошибка при обнаружении игры: {e}")
            return None
            
    def _get_active_window(self) -> Optional[Dict]:
        """Получить информацию об активном окне"""
        try:
            if self.platform == "Windows" and WINDOWS_AVAILABLE:
                hwnd = win32gui.GetForegroundWindow()
                if hwnd:
                    window_title = win32gui.GetWindowText(hwnd)
                    return {
                        "title": window_title,
                        "hwnd": hwnd
                    }
                    
            elif self.platform == "Darwin" and MACOS_AVAILABLE:
                active_app = AppKit.NSWorkspace.sharedWorkspace().activeApplication()
                if active_app:
                    return {
                        "title": active_app['NSApplicationName'],
                        "bundle_id": active_app.get('NSApplicationBundleIdentifier', '')
                    }
                    
            elif self.platform == "Linux" and LINUX_AVAILABLE:
                display = Xlib.display.Display()
                root = display.screen().root
                window = root.get_active_window()
                if window:
                    window_title = window.get_wm_name()
                    return {
                        "title": window_title,
                        "window_id": window.id
                    }
                    
        except Exception as e:
            print(f"Ошибка получения активного окна: {e}")
            
        return None
        
    def _check_process_for_game(self, process_name: str, active_window: Dict, pid: int) -> Optional[GameInfo]:
        """Проверить процесс на соответствие игре"""
        for game_name, game_config in self.supported_games.items():
            # Проверка по имени процесса
            process_match = any(proc_name.lower() in process_name for proc_name in game_config["process_names"])
            
            # Проверка по заголовку окна
            window_title = active_window.get("title", "").lower()
            window_match = any(title.lower() in window_title for title in game_config["window_titles"])
            
            # Расчет уверенности
            confidence = 0.0
            if process_match:
                confidence += game_config["confidence"] * 0.7
            if window_match:
                confidence += game_config["confidence"] * 0.3
                
            # Если уверенность достаточна
            if confidence >= 0.5:
                return GameInfo(
                    name=game_name,
                    process_name=process_name,
                    window_title=active_window.get("title", ""),
                    confidence=confidence,
                    pid=pid,
                    start_time=time.time()
                )
                
        return None
        
    def start_monitoring(self, callback: Optional[callable] = None):
        """Начать мониторинг активных игр"""
        if self.is_monitoring:
            return
            
        self.is_monitoring = True
        self.stop_event.clear()
        
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            args=(callback,)
        )
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
        
        print("🎮 Начат мониторинг игр...")
        
    def stop_monitoring(self):
        """Остановить мониторинг"""
        if not self.is_monitoring:
            return
            
        self.is_monitoring = False
        self.stop_event.set()
        
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=2.0)
            
        print("🛑 Мониторинг игр остановлен")
        
    def _monitoring_loop(self, callback: Optional[callable]):
        """Цикл мониторинга игр"""
        time.sleep(2.0) # Критически важно: ждем отрисовки интерфейса
        while not self.stop_event.is_set():
            current_time = time.time()
            
            # Проверяем с заданным интервалом
            if current_time - self.last_check_time >= self.check_interval:
                game_info = self.detect_current_game()
                
                # Логика определения изменения игры
                is_changed = False
                if game_info and not self.current_game:
                    is_changed = True
                elif game_info and self.current_game and game_info.name != self.current_game.name:
                    is_changed = True
                elif not game_info and self.current_game:
                    # Игра закрылась
                    self.current_game = None
                
                # Вызываем callback если игра изменилась
                if is_changed and callback:
                    self.current_game = game_info
                    callback(game_info)
                    
                self.last_check_time = current_time
                
            time.sleep(0.1)  # Не нагружаем CPU
            
    def get_game_profile(self, game_name: str) -> Optional[Dict]:
        """Получить профиль игры"""
        return self.supported_games.get(game_name)
        
    def add_game(self, game_name: str, process_names: List[str], 
                window_titles: List[str], confidence: float = 0.8,
                game_type: str = "unknown", category: str = "unknown"):
        """Добавить новую игру в список поддерживаемых"""
        self.supported_games[game_name] = {
            "process_names": process_names,
            "window_titles": window_titles,
            "confidence": confidence,
            "game_type": game_type,
            "category": category
        }
        
    def remove_game(self, game_name: str):
        """Удалить игру из списка поддерживаемых"""
        if game_name in self.supported_games:
            del self.supported_games[game_name]
            
    def get_detection_stats(self) -> Dict:
        """Получить статистику обнаружения"""
        total = self.detection_stats["total_checks"]
        detected = self.detection_stats["games_detected"]
        
        if total > 0:
            detection_rate = (detected / total) * 100
        else:
            detection_rate = 0.0
            
        return {
            **self.detection_stats,
            "detection_rate": detection_rate,
            "current_game": self.current_game.name if self.current_game else None
        }
        
    def get_current_game_info(self) -> Optional[GameInfo]:
        """Получить информацию о текущей игре"""
        return self.current_game
        
    def is_game_running(self, game_name: str) -> bool:
        """Проверить, запущена ли игра"""
        if not self.is_game_supported(game_name):
            return False
            
        try:
            game_config = self.supported_games[game_name]
            
            for proc in psutil.process_iter(['name']):
                try:
                    process_name = proc.info['name'].lower()
                    if any(proc_name.lower() in process_name for proc_name in game_config["process_names"]):
                        return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
                    
        except Exception:
            pass
            
        return False

def create_game_detector():
    """Factory for creating game detector"""
    return GameDetector()

# Пример использования
if __name__ == "__main__":
    detector = create_game_detector()
    
    print("🎮 Тестирование GameDetector...")
    print(f"Платформа: {detector.platform}")
    print(f"Поддерживаемые игры: {detector.get_supported_games()}")
    
    # Тест одиночного обнаружения
    print("\n🔍 Одиночное обнаружение:")
    game = detector.detect_current_game()
    if game:
        print(f"   Найдена игра: {game.name}")
        print(f"   Процесс: {game.process_name}")
        print(f"   Окно: {game.window_title}")
        print(f"   Уверенность: {game.confidence:.2f}")
    else:
        print("   Игра не найдена")
        
    # Тест мониторинга (5 секунд)
    print("\n📊 Тест мониторинга (5 секунд)...")
    
    def on_game_change(game_info):
        print(f"   🎮 Изменение: {game_info.name} (уверенность: {game_info.confidence:.2f})")
        
    detector.start_monitoring(on_game_change)
    time.sleep(5)
    detector.stop_monitoring()
    
    # Статистика
    stats = detector.get_detection_stats()
    print(f"\n📈 Статистика:")
    print(f"   Всего проверок: {stats['total_checks']}")
    print(f"   Игр обнаружено: {stats['games_detected']}")
    print(f"   Процент обнаружения: {stats['detection_rate']:.1f}%")