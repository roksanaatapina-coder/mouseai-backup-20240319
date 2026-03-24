#!/usr/bin/env python3
"""
Auto Session Manager - Автоматическое управление сессиями
"""

import asyncio
import logging
from typing import Dict, List, Optional, Callable
from datetime import datetime, timedelta
import json
import threading
import time

class AutoSessionManager:
    """Менеджер автоматических сессий"""
    
    def __init__(self, mouseai_instance=None):
        self.mouseai = mouseai_instance
        self.logger = logging.getLogger(__name__)
        
        # Конфигурация
        self.config = {
            'enabled': False,
            'schedule': [],  # Расписание сессий
            'auto_start': True,
            'auto_stop': True,
            'session_duration': 300,  # 5 минут по умолчанию
            'games': ['CS2', 'PUBG', 'Valorant'],
            'analysis_type': 'quick',
            'break_between_sessions': 60,  # Перерыв между сессиями
            'max_daily_sessions': 10,
            'active_days': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        }
        
        # Состояние
        self.is_running = False
        self.current_session = None
        self.session_history = []
        self.daily_session_count = 0
        self.last_session_time = None
        
        # Коллбэки
        self.on_session_start = None
        self.on_session_end = None
        self.on_session_complete = None
        
        # Потоки
        self.scheduler_thread = None
        self.monitor_thread = None
        
    def configure(self, config: Dict):
        """Настроить менеджер сессий"""
        self.config.update(config)
        self.logger.info(f"Авто-сессии настроены: {config}")
        
    def start(self):
        """Запустить автоматическое управление сессиями"""
        if not self.config.get('enabled', False):
            self.logger.warning("Авто-сессии отключены в конфигурации")
            return False
            
        if not self.mouseai:
            self.logger.error("MouseAI не подключен")
            return False
            
        self.is_running = True
        
        # Запускаем потоки
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.scheduler_thread.start()
        
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        self.logger.info("Авто-сессии запущены")
        return True
        
    def stop(self):
        """Остановить автоматическое управление сессиями"""
        self.is_running = False
        
        if self.current_session:
            self.stop_current_session()
            
        self.logger.info("Авто-сессии остановлены")
        
    def add_schedule(self, day: str, time_str: str, game: str = None, duration: int = None):
        """Добавить расписание сессии"""
        schedule_item = {
            'day': day,
            'time': time_str,
            'game': game or self.config['games'][0],
            'duration': duration or self.config['session_duration']
        }
        
        self.config['schedule'].append(schedule_item)
        self.logger.info(f"Добавлено расписание: {schedule_item}")
        
    def remove_schedule(self, day: str, time_str: str):
        """Удалить расписание сессии"""
        self.config['schedule'] = [
            s for s in self.config['schedule'] 
            if not (s['day'] == day and s['time'] == time_str)
        ]
        self.logger.info(f"Удалено расписание: {day} {time_str}")
        
    def get_next_session_time(self) -> Optional[datetime]:
        """Получить время следующей сессии"""
        now = datetime.now()
        current_day = now.strftime('%A')
        current_time = now.time()
        
        # Сначала ищем в текущий день
        for schedule_item in self.config['schedule']:
            if schedule_item['day'] == current_day:
                session_time = datetime.strptime(schedule_item['time'], '%H:%M').time()
                if session_time > current_time:
                    return datetime.combine(now.date(), session_time)
                    
        # Если в текущий день нет, ищем в следующие дни
        days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        current_day_index = days_of_week.index(current_day)
        
        for i in range(1, 8):
            next_day_index = (current_day_index + i) % 7
            next_day = days_of_week[next_day_index]
            
            if next_day in self.config['active_days']:
                for schedule_item in self.config['schedule']:
                    if schedule_item['day'] == next_day:
                        session_time = datetime.strptime(schedule_item['time'], '%H:%M').time()
                        next_date = now.date() + timedelta(days=i)
                        return datetime.combine(next_date, session_time)
                        
        return None
        
    def start_session_now(self, game: str = None, duration: int = None):
        """Начать сессию немедленно"""
        if self.daily_session_count >= self.config['max_daily_sessions']:
            self.logger.warning("Достигнуто максимальное количество сессий за день")
            return False
            
        if self.current_session:
            self.logger.warning("Сессия уже запущена")
            return False
            
        game = game or self.config['games'][0]
        duration = duration or self.config['session_duration']
        
        try:
            self.current_session = {
                'game': game,
                'duration': duration,
                'start_time': datetime.now(),
                'status': 'running'
            }
            
            self.mouseai.start_session(game, duration)
            self.daily_session_count += 1
            self.last_session_time = datetime.now()
            
            if self.on_session_start:
                self.on_session_start(self.current_session)
                
            self.logger.info(f"Сессия начата: {game} на {duration} сек")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка запуска сессии: {e}")
            self.current_session = None
            return False
            
    def stop_current_session(self):
        """Остановить текущую сессию"""
        if not self.current_session:
            return False
            
        try:
            self.mouseai.stop_session()
            
            session_data = self.current_session.copy()
            session_data['end_time'] = datetime.now()
            session_data['status'] = 'completed'
            
            self.session_history.append(session_data)
            self.current_session = None
            
            if self.on_session_end:
                self.on_session_end(session_data)
                
            self.logger.info("Сессия остановлена")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка остановки сессии: {e}")
            return False
            
    def _scheduler_loop(self):
        """Цикл планировщика сессий"""
        while self.is_running:
            try:
                if self.current_session:
                    # Ждем завершения текущей сессии
                    time.sleep(10)
                    continue
                    
                # Проверяем, нужно ли начать сессию
                next_session_time = self.get_next_session_time()
                
                if next_session_time:
                    time_until_next = (next_session_time - datetime.now()).total_seconds()
                    
                    if 0 <= time_until_next <= 60:  # Сессия должна начаться в течение минуты
                        # Находим подходящее расписание
                        for schedule_item in self.config['schedule']:
                            if (schedule_item['day'] == next_session_time.strftime('%A') and
                                schedule_item['time'] == next_session_time.strftime('%H:%M')):
                                
                                if self.daily_session_count < self.config['max_daily_sessions']:
                                    self.start_session_now(
                                        schedule_item['game'], 
                                        schedule_item['duration']
                                    )
                                break
                                
                time.sleep(60)  # Проверяем каждую минуту
                
            except Exception as e:
                self.logger.error(f"Ошибка в планировщике: {e}")
                time.sleep(60)
                
    def _monitor_loop(self):
        """Цикл мониторинга сессий"""
        while self.is_running:
            try:
                if self.current_session:
                    # Проверяем, нужно ли остановить сессию
                    elapsed = (datetime.now() - self.current_session['start_time']).total_seconds()
                    
                    if elapsed >= self.current_session['duration']:
                        self.stop_current_session()
                        
                    # Проверяем активность мыши
                    if self._check_mouse_activity():
                        self.current_session['last_activity'] = datetime.now()
                    else:
                        # Если нет активности, увеличиваем таймер бездействия
                        last_activity = self.current_session.get('last_activity', self.current_session['start_time'])
                        inactive_time = (datetime.now() - last_activity).total_seconds()
                        
                        if inactive_time > 300:  # 5 минут бездействия
                            self.logger.warning("Обнаружено длительное бездействие мыши")
                            if self.on_session_end:
                                self.on_session_end({
                                    'game': self.current_session['game'],
                                    'reason': 'inactive',
                                    'duration': elapsed
                                })
                            self.current_session = None
                            
                time.sleep(10)  # Проверяем каждые 10 секунд
                
            except Exception as e:
                self.logger.error(f"Ошибка в мониторинге: {e}")
                time.sleep(10)
                
    def _check_mouse_activity(self) -> bool:
        """Проверить активность мыши"""
        try:
            # Получаем последние данные о мыши
            current_metrics = self.mouseai.get_current_metrics()
            
            if current_metrics and 'sample_entropy' in current_metrics:
                # Если есть активность (Sample Entropy > 0.1)
                return current_metrics['sample_entropy'] > 0.1
                
            return False
            
        except Exception:
            return False
            
    def get_status(self) -> Dict:
        """Получить статус менеджера сессий"""
        return {
            'enabled': self.config.get('enabled', False),
            'is_running': self.is_running,
            'current_session': self.current_session,
            'daily_session_count': self.daily_session_count,
            'max_daily_sessions': self.config['max_daily_sessions'],
            'next_session_time': self.get_next_session_time().isoformat() if self.get_next_session_time() else None,
            'session_history_count': len(self.session_history)
        }
        
    def get_session_history(self, limit: int = 10) -> List[Dict]:
        """Получить историю сессий"""
        return self.session_history[-limit:]
        
    def reset_daily_counter(self):
        """Сбросить счетчик дневных сессий"""
        self.daily_session_count = 0
        self.logger.info("Счетчик дневных сессий сброшен")
        
    def export_schedule(self, filename: str):
        """Экспортировать расписание"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
            
    def import_schedule(self, filename: str):
        """Импортировать расписание"""
        with open(filename, 'r', encoding='utf-8') as f:
            config = json.load(f)
            self.config.update(config)

def create_auto_session_manager(mouseai_instance=None) -> AutoSessionManager:
    """Создать менеджер автоматических сессий"""
    return AutoSessionManager(mouseai_instance)