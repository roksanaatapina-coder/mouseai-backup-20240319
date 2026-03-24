#!/usr/bin/env python3
"""
MouseAI Config - Конфигурация системы
"""

import json
import os
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime

class MouseAIConfig:
    """Класс управления конфигурацией"""
    
    def __init__(self, config_file: str = 'mouseai_config.json'):
        self.config_file = config_file
        self.logger = logging.getLogger(__name__)
        
        # Конфигурация по умолчанию
        self.default_config = {
            # Общие настройки
            'general': {
                'version': '1.0.0',
                'language': 'ru',
                'theme': 'dark',
                'auto_start': False,
                'auto_update': True,
                'check_updates': True,
                'send_analytics': False,
                'data_path': 'data/',
                'backup_path': 'backups/',
                'log_level': 'INFO',
                'max_log_files': 10,
                'log_rotation': True
            },
            
            # Настройки сбора данных
            'collection': {
                'enabled': True,
                'frequency': 120,  # Гц
                'buffer_size': 1000,
                'save_raw_data': True,
                'save_processed_data': True,
                'compression': True,
                'format': 'json',
                'retention_days': 90,
                'auto_clean': True,
                'noise_filter': True,
                'smoothing_factor': 0.5,
                'calibration_enabled': True,
                'min_movement_threshold': 1.0
            },
            
            # Настройки анализа
            'analysis': {
                'enabled': True,
                'method': 'scientific',  # scientific, ml, hybrid
                'accuracy': 'medium',  # low, medium, high, ultra
                'auto_analyze': True,
                'real_time_analysis': True,
                'batch_size': 100,
                'metrics': [
                    'sample_entropy',
                    'maximum_absolute_deviation',
                    'time_to_peak_velocity',
                    'movement_efficiency',
                    'jerk_metrics',
                    'frequency_analysis'
                ],
                'ml_algorithms': [
                    'random_forest',
                    'svm',
                    'neural_network'
                ],
                'pattern_recognition': True,
                'anomaly_detection': True,
                'trend_analysis': True
            },
            
            # Настройки визуализации
            'visualization': {
                'enabled': True,
                'theme': 'default',
                'update_interval': 5,  # секунды
                'resolution': 'medium',
                'color_scheme': 'thermal',
                'show_grid': True,
                'show_legend': True,
                'auto_scale': True,
                'export_format': 'png',
                'export_quality': 'high',
                'dashboard_refresh': 10
            },
            
            # Настройки игр
            'games': {
                'supported_games': [
                    'CS2', 'PUBG', 'Valorant', 'Overwatch', 'Rainbow Six Siege',
                    'Call of Duty: Warzone', 'Fortnite', 'Apex Legends',
                    'Escape from Tarkov', 'Rainbow Six Extraction'
                ],
                'auto_detect': True,
                'game_specific_settings': {},
                'sensitivity_profiles': {},
                'aim_assist_detection': True,
                'crosshair_tracking': True
            },
            
            # Настройки интеграций
            'integrations': {
                'discord': {
                    'enabled': False,
                    'token': '',
                    'channel_id': '',
                    'notifications': {
                        'session_start': True,
                        'session_end': True,
                        'anomalies': True,
                        'achievements': True
                    }
                },
                'telegram': {
                    'enabled': False,
                    'token': '',
                    'chat_id': '',
                    'notifications': {
                        'session_start': True,
                        'session_end': True,
                        'anomalies': True,
                        'reports': True
                    }
                },
                'obs': {
                    'enabled': False,
                    'port': 8765,
                    'websocket_enabled': True,
                    'overlay_theme': 'dark',
                    'metrics_display': ['sample_entropy', 'efficiency', 'reaction_time']
                },
                'rest_api': {
                    'enabled': False,
                    'port': 5000,
                    'host': 'localhost',
                    'auth_required': False,
                    'api_key': '',
                    'cors_enabled': True
                }
            },
            
            # Настройки автоматизации
            'automation': {
                'auto_session_manager': {
                    'enabled': False,
                    'schedule': [],
                    'auto_start': True,
                    'auto_stop': True,
                    'break_between_sessions': 60,
                    'max_daily_sessions': 10
                },
                'auto_analyzer': {
                    'enabled': False,
                    'analysis_interval': 300,
                    'auto_generate_reports': True,
                    'trend_analysis': True,
                    'anomaly_detection': True
                },
                'auto_updater': {
                    'enabled': True,
                    'check_interval': 3600,
                    'auto_download': True,
                    'auto_install': False,
                    'update_channel': 'stable'
                }
            },
            
            # Настройки производительности
            'performance': {
                'cpu_limit': 50,  # процент
                'memory_limit': 1024,  # МБ
                'priority': 'normal',  # low, normal, high, realtime
                'background_processing': True,
                'gpu_acceleration': False,
                'thread_count': 4
            },
            
            # Настройки безопасности
            'security': {
                'data_encryption': False,
                'backup_encryption': False,
                'api_auth': False,
                'firewall_enabled': False,
                'privacy_mode': False
            },
            
            # Настройки пользовательского интерфейса
            'ui': {
                'window_size': {'width': 1000, 'height': 700},
                'window_position': {'x': 100, 'y': 100},
                'font_size': 12,
                'font_family': 'Segoe UI',
                'show_tooltips': True,
                'show_welcome_screen': True,
                'recent_files_limit': 10,
                'auto_save': True,
                'auto_save_interval': 300
            }
        }
        
        # Загружаем конфигурацию
        self.config = self.load_config()
        
    def load_config(self) -> Dict[str, Any]:
        """Загрузить конфигурацию из файла"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    
                # Объединяем с дефолтной конфигурацией
                config = self._merge_configs(self.default_config, loaded_config)
                self.logger.info("Конфигурация загружена")
                return config
            else:
                # Создаем файл с дефолтной конфигурацией
                self.save_config()
                return self.default_config
                
        except Exception as e:
            self.logger.error(f"Ошибка загрузки конфигурации: {e}")
            return self.default_config
            
    def save_config(self, config: Dict[str, Any] = None):
        """Сохранить конфигурацию в файл"""
        try:
            if config is None:
                config = self.config
                
            # Создаем директорию, если она не существует
            Path(self.config_file).parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
                
            self.logger.info("Конфигурация сохранена")
            
        except Exception as e:
            self.logger.error(f"Ошибка сохранения конфигурации: {e}")
            
    def get(self, key: str, default: Any = None) -> Any:
        """Получить значение из конфигурации"""
        try:
            keys = key.split('.')
            value = self.config
            
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default
                    
            return value
            
        except Exception:
            return default
            
    def set(self, key: str, value: Any):
        """Установить значение в конфигурации"""
        try:
            keys = key.split('.')
            config = self.config
            
            for k in keys[:-1]:
                if k not in config:
                    config[k] = {}
                config = config[k]
                
            config[keys[-1]] = value
            self.save_config()
            
        except Exception as e:
            self.logger.error(f"Ошибка установки конфигурации: {e}")
            
    def update(self, updates: Dict[str, Any]):
        """Обновить конфигурацию"""
        try:
            self.config = self._merge_configs(self.config, updates)
            self.save_config()
            self.logger.info("Конфигурация обновлена")
            
        except Exception as e:
            self.logger.error(f"Ошибка обновления конфигурации: {e}")
            
    def reset_to_defaults(self):
        """Сбросить конфигурацию до значений по умолчанию"""
        self.config = self.default_config.copy()
        self.save_config()
        self.logger.info("Конфигурация сброшена до значений по умолчанию")
        
    def export_config(self, filename: str):
        """Экспортировать конфигурацию"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Конфигурация экспортирована в {filename}")
            
        except Exception as e:
            self.logger.error(f"Ошибка экспорта конфигурации: {e}")
            
    def import_config(self, filename: str):
        """Импортировать конфигурацию"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                imported_config = json.load(f)
                
            self.config = self._merge_configs(self.default_config, imported_config)
            self.save_config()
            self.logger.info(f"Конфигурация импортирована из {filename}")
            
        except Exception as e:
            self.logger.error(f"Ошибка импорта конфигурации: {e}")
            
    def validate_config(self) -> Dict[str, List[str]]:
        """Проверить валидность конфигурации"""
        errors = []
        warnings = []
        
        # Проверка частоты сбора данных
        frequency = self.get('collection.frequency', 120)
        if frequency < 30 or frequency > 1000:
            errors.append("Частота сбора данных должна быть в диапазоне 30-1000 Гц")
            
        # Проверка уровня логирования
        log_level = self.get('general.log_level', 'INFO')
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR']
        if log_level not in valid_levels:
            errors.append(f"Неверный уровень логирования: {log_level}")
            
        # Проверка пути для данных
        data_path = self.get('general.data_path', 'data/')
        if not data_path:
            errors.append("Путь для данных не может быть пустым")
            
        # Проверка настроек производительности
        cpu_limit = self.get('performance.cpu_limit', 50)
        if cpu_limit < 10 or cpu_limit > 100:
            warnings.append("Рекомендуется установить CPU лимит в диапазоне 10-100%")
            
        memory_limit = self.get('performance.memory_limit', 1024)
        if memory_limit < 100:
            warnings.append("Рекомендуется выделить больше памяти для работы системы")
            
        return {'errors': errors, 'warnings': warnings}
        
    def get_section(self, section: str) -> Dict[str, Any]:
        """Получить секцию конфигурации"""
        return self.config.get(section, {})
        
    def get_game_config(self, game: str) -> Dict[str, Any]:
        """Получить конфигурацию для конкретной игры"""
        game_configs = self.get('games.game_specific_settings', {})
        return game_configs.get(game, {})
        
    def set_game_config(self, game: str, config: Dict[str, Any]):
        """Установить конфигурацию для конкретной игры"""
        game_configs = self.get('games.game_specific_settings', {})
        game_configs[game] = config
        self.set('games.game_specific_settings', game_configs)
        
    def add_sensitivity_profile(self, name: str, profile: Dict[str, Any]):
        """Добавить профиль чувствительности"""
        profiles = self.get('games.sensitivity_profiles', {})
        profiles[name] = profile
        self.set('games.sensitivity_profiles', profiles)
        
    def get_sensitivity_profile(self, name: str) -> Optional[Dict[str, Any]]:
        """Получить профиль чувствительности"""
        profiles = self.get('games.sensitivity_profiles', {})
        return profiles.get(name)
        
    def get_supported_games(self) -> List[str]:
        """Получить список поддерживаемых игр"""
        return self.get('games.supported_games', [])
        
    def add_supported_game(self, game: str):
        """Добавить поддерживаемую игру"""
        games = self.get_supported_games()
        if game not in games:
            games.append(game)
            self.set('games.supported_games', games)
            
    def remove_supported_game(self, game: str):
        """Удалить поддерживаемую игру"""
        games = self.get_supported_games()
        if game in games:
            games.remove(game)
            self.set('games.supported_games', games)
            
    def get_integration_config(self, integration: str) -> Dict[str, Any]:
        """Получить конфигурацию интеграции"""
        return self.get(f'integrations.{integration}', {})
        
    def enable_integration(self, integration: str, enabled: bool = True):
        """Включить/выключить интеграцию"""
        self.set(f'integrations.{integration}.enabled', enabled)
        
    def get_performance_stats(self) -> Dict[str, Any]:
        """Получить статистику производительности"""
        return {
            'cpu_limit': self.get('performance.cpu_limit'),
            'memory_limit': self.get('performance.memory_limit'),
            'priority': self.get('performance.priority'),
            'thread_count': self.get('performance.thread_count'),
            'background_processing': self.get('performance.background_processing'),
            'gpu_acceleration': self.get('performance.gpu_acceleration')
        }
        
    def get_ui_settings(self) -> Dict[str, Any]:
        """Получить настройки интерфейса"""
        return self.get('ui', {})
        
    def get_analysis_settings(self) -> Dict[str, Any]:
        """Получить настройки анализа"""
        return self.get('analysis', {})
        
    def get_collection_settings(self) -> Dict[str, Any]:
        """Получить настройки сбора данных"""
        return self.get('collection', {})
        
    def get_visualization_settings(self) -> Dict[str, Any]:
        """Получить настройки визуализации"""
        return self.get('visualization', {})
        
    def _merge_configs(self, default: Dict, override: Dict) -> Dict:
        """Рекурсивно объединить конфигурации"""
        result = default.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
                
        return result
        
    def get_config_summary(self) -> Dict[str, Any]:
        """Получить краткую сводку конфигурации"""
        return {
            'version': self.get('general.version'),
            'language': self.get('general.language'),
            'theme': self.get('general.theme'),
            'data_collection_enabled': self.get('collection.enabled'),
            'analysis_enabled': self.get('analysis.enabled'),
            'visualization_enabled': self.get('visualization.enabled'),
            'supported_games_count': len(self.get_supported_games()),
            'integrations_enabled': [
                name for name, config in self.get('integrations', {}).items()
                if config.get('enabled', False)
            ],
            'automation_enabled': any([
                self.get('automation.auto_session_manager.enabled'),
                self.get('automation.auto_analyzer.enabled'),
                self.get('automation.auto_updater.enabled')
            ])
        }

def create_config(config_file: str = 'mouseai_config.json') -> MouseAIConfig:
    """Создать экземпляр конфигурации"""
    return MouseAIConfig(config_file)