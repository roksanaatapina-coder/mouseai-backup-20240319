#!/usr/bin/env python3
"""
Auto Updater - Автоматическое обновление системы
"""

import asyncio
import logging
import requests
import json
import os
import sys
import subprocess
import threading
import time
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import hashlib
import zipfile
import tempfile

class AutoUpdater:
    """Автоматический обновлятор системы"""
    
    def __init__(self, mouseai_instance=None):
        self.mouseai = mouseai_instance
        self.logger = logging.getLogger(__name__)
        
        # Конфигурация
        self.config = {
            'enabled': True,
            'check_interval': 3600,  # Проверять обновления каждый час
            'auto_download': True,
            'auto_install': False,  # Требовать подтверждения по умолчанию
            'update_channel': 'stable',  # stable, beta, alpha
            'backup_before_update': True,
            'rollback_on_failure': True,
            'update_server': 'https://api.mouseai.com',
            'check_ssl': True
        }
        
        # Состояние
        self.is_running = False
        self.current_version = self._get_current_version()
        self.latest_version = None
        self.update_available = False
        self.update_info = None
        self.download_progress = 0
        self.is_downloading = False
        self.is_installing = False
        
        # Коллбэки
        self.on_update_available = None
        self.on_download_complete = None
        self.on_install_complete = None
        self.on_error = None
        
        # Потоки
        self.checker_thread = None
        self.downloader_thread = None
        
    def configure(self, config: Dict):
        """Настроить обновлятор"""
        self.config.update(config)
        self.logger.info(f"Авто-обновление настроено: {config}")
        
    def start(self):
        """Запустить автоматическую проверку обновлений"""
        if not self.config.get('enabled', True):
            self.logger.warning("Авто-обновление отключено в конфигурации")
            return False
            
        self.is_running = True
        
        # Запускаем поток проверки
        self.checker_thread = threading.Thread(target=self._check_loop, daemon=True)
        self.checker_thread.start()
        
        self.logger.info("Авто-обновление запущено")
        return True
        
    def stop(self):
        """Остановить автоматическую проверку обновлений"""
        self.is_running = False
        self.logger.info("Авто-обновление остановлено")
        
    def check_for_updates(self) -> Dict:
        """Проверить наличие обновлений"""
        try:
            # Получаем информацию о последней версии
            update_info = self._fetch_update_info()
            
            if update_info:
                self.latest_version = update_info.get('version')
                self.update_info = update_info
                
                # Сравниваем версии
                if self._is_newer_version(self.latest_version, self.current_version):
                    self.update_available = True
                    
                    result = {
                        'update_available': True,
                        'current_version': self.current_version,
                        'latest_version': self.latest_version,
                        'update_info': update_info
                    }
                    
                    if self.on_update_available:
                        self.on_update_available(update_info)
                        
                    return result
                else:
                    self.update_available = False
                    return {
                        'update_available': False,
                        'current_version': self.current_version,
                        'latest_version': self.latest_version
                    }
            else:
                return {'error': 'Не удалось получить информацию об обновлениях'}
                
        except Exception as e:
            self.logger.error(f"Ошибка проверки обновлений: {e}")
            if self.on_error:
                self.on_error(str(e))
            return {'error': str(e)}
            
    def download_update(self, update_info: Dict = None):
        """Скачать обновление"""
        if not update_info:
            update_info = self.update_info
            
        if not update_info:
            self.logger.error("Нет информации об обновлении")
            return False
            
        download_url = update_info.get('download_url')
        if not download_url:
            self.logger.error("Нет URL для скачивания обновления")
            return False
            
        self.is_downloading = True
        self.download_progress = 0
        
        # Запускаем скачивание в фоновом потоке
        self.downloader_thread = threading.Thread(
            target=self._download_update_thread, 
            args=(download_url,), 
            daemon=True
        )
        self.downloader_thread.start()
        
        return True
        
    def install_update(self, update_file: str):
        """Установить обновление"""
        if self.is_installing:
            self.logger.warning("Установка уже выполняется")
            return False
            
        self.is_installing = True
        
        try:
            # Создаем резервную копию
            if self.config['backup_before_update']:
                self._create_backup()
                
            # Устанавливаем обновление
            success = self._install_update_file(update_file)
            
            if success:
                if self.on_install_complete:
                    self.on_install_complete(self.latest_version)
                self.logger.info(f"Обновление установлено: {self.latest_version}")
            else:
                # Откатываемся при неудаче
                if self.config['rollback_on_failure']:
                    self._rollback_update()
                self.logger.error("Установка обновления не удалась")
                
            self.is_installing = False
            return success
            
        except Exception as e:
            self.logger.error(f"Ошибка установки обновления: {e}")
            if self.on_error:
                self.on_error(str(e))
            self.is_installing = False
            return False
            
    def _check_loop(self):
        """Цикл проверки обновлений"""
        while self.is_running:
            try:
                # Проверяем обновления
                result = self.check_for_updates()
                
                # Автоматическое скачивание, если включено
                if (result.get('update_available') and 
                    self.config['auto_download'] and 
                    not self.is_downloading):
                    self.download_update(result.get('update_info'))
                    
                # Автоматическая установка, если включена
                if (result.get('update_available') and 
                    self.config['auto_install'] and 
                    self.download_progress == 100):
                    # Здесь нужно знать путь к скачанному файлу
                    # Пока пропускаем автоматическую установку
                    pass
                    
                # Ждем интервал
                time.sleep(self.config['check_interval'])
                
            except Exception as e:
                self.logger.error(f"Ошибка в цикле проверки: {e}")
                time.sleep(3600)  # Пауза при ошибке
                
    def _fetch_update_info(self) -> Optional[Dict]:
        """Получить информацию об обновлении"""
        try:
            url = f"{self.config['update_server']}/api/updates/latest"
            params = {
                'version': self.current_version,
                'channel': self.config['update_channel'],
                'platform': sys.platform
            }
            
            response = requests.get(
                url, 
                params=params, 
                timeout=30,
                verify=self.config['check_ssl']
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                self.logger.warning(f"Ошибка получения обновлений: {response.status_code}")
                return None
                
        except Exception as e:
            self.logger.error(f"Ошибка запроса к серверу обновлений: {e}")
            return None
            
    def _is_newer_version(self, version1: str, version2: str) -> bool:
        """Проверить, является ли версия1 новее версии2"""
        try:
            v1_parts = [int(x) for x in version1.split('.')]
            v2_parts = [int(x) for x in version2.split('.')]
            
            # Дополняем нулями до одинаковой длины
            max_len = max(len(v1_parts), len(v2_parts))
            v1_parts.extend([0] * (max_len - len(v1_parts)))
            v2_parts.extend([0] * (max_len - len(v2_parts)))
            
            # Сравниваем по частям
            for v1, v2 in zip(v1_parts, v2_parts):
                if v1 > v2:
                    return True
                elif v1 < v2:
                    return False
                    
            return False  # Версии одинаковые
            
        except Exception:
            # Если не удалось распарсить версии, сравниваем как строки
            return version1 > version2
            
    def _download_update_thread(self, download_url: str):
        """Поток скачивания обновления"""
        try:
            response = requests.get(download_url, stream=True, timeout=30)
            total_size = int(response.headers.get('content-length', 0))
            
            # Создаем временный файл
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
            
            downloaded = 0
            chunk_size = 8192
            
            with temp_file:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        temp_file.write(chunk)
                        downloaded += len(chunk)
                        
                        if total_size > 0:
                            self.download_progress = (downloaded / total_size) * 100
                            
            self.is_downloading = False
            
            if self.on_download_complete:
                self.on_download_complete(temp_file.name, self.download_progress)
                
            self.logger.info(f"Скачивание завершено: {temp_file.name}")
            
        except Exception as e:
            self.logger.error(f"Ошибка скачивания: {e}")
            self.is_downloading = False
            if self.on_error:
                self.on_error(str(e))
                
    def _create_backup(self):
        """Создать резервную копию"""
        try:
            backup_dir = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            os.makedirs(backup_dir, exist_ok=True)
            
            # Копируем основные файлы
            import shutil
            main_dir = os.path.dirname(os.path.abspath(__file__))
            
            # Копируем папку mouseai
            mouseai_src = os.path.join(main_dir, 'mouseai')
            mouseai_backup = os.path.join(backup_dir, 'mouseai')
            if os.path.exists(mouseai_src):
                shutil.copytree(mouseai_src, mouseai_backup, dirs_exist_ok=True)
                
            # Копируем конфигурационные файлы
            config_files = ['mouseai_config.json', 'settings.json']
            for config_file in config_files:
                if os.path.exists(config_file):
                    shutil.copy2(config_file, backup_dir)
                    
            self.logger.info(f"Резервная копия создана: {backup_dir}")
            
        except Exception as e:
            self.logger.error(f"Ошибка создания резервной копии: {e}")
            
    def _install_update_file(self, update_file: str) -> bool:
        """Установить файл обновления"""
        try:
            # Распаковываем архив
            with zipfile.ZipFile(update_file, 'r') as zip_ref:
                extract_path = os.path.dirname(os.path.abspath(__file__))
                zip_ref.extractall(extract_path)
                
            # Проверяем целостность
            if self._verify_update():
                self.current_version = self.latest_version
                return True
            else:
                self.logger.error("Целостность обновления не подтверждена")
                return False
                
        except Exception as e:
            self.logger.error(f"Ошибка установки обновления: {e}")
            return False
            
    def _verify_update(self) -> bool:
        """Проверить целостность обновления"""
        try:
            # Проверяем наличие основных файлов
            required_files = [
                'mouseai/core/__init__.py',
                'mouseai/analysis/__init__.py',
                'mouseai/visualization/__init__.py'
            ]
            
            main_dir = os.path.dirname(os.path.abspath(__file__))
            
            for file_path in required_files:
                full_path = os.path.join(main_dir, file_path)
                if not os.path.exists(full_path):
                    self.logger.error(f"Отсутствует файл: {file_path}")
                    return False
                    
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка проверки целостности: {e}")
            return False
            
    def _rollback_update(self):
        """Откатить обновление"""
        try:
            # Ищем последнюю резервную копию
            backup_dirs = [d for d in os.listdir('.') if d.startswith('backup_')]
            if not backup_dirs:
                self.logger.error("Нет резервных копий для отката")
                return False
                
            latest_backup = sorted(backup_dirs)[-1]
            backup_path = os.path.join(latest_backup, 'mouseai')
            
            if os.path.exists(backup_path):
                import shutil
                main_dir = os.path.dirname(os.path.abspath(__file__))
                current_mouseai = os.path.join(main_dir, 'mouseai')
                
                # Удаляем текущую папку
                shutil.rmtree(current_mouseai)
                # Восстанавливаем из резервной копии
                shutil.copytree(backup_path, current_mouseai)
                
                self.logger.info(f"Откат выполнен из {latest_backup}")
                return True
            else:
                self.logger.error("Резервная копия не найдена")
                return False
                
        except Exception as e:
            self.logger.error(f"Ошибка отката: {e}")
            return False
            
    def _get_current_version(self) -> str:
        """Получить текущую версию"""
        try:
            # Пытаемся получить версию из setup.py или version.py
            version_file = os.path.join(os.path.dirname(__file__), '..', '..', 'version.py')
            if os.path.exists(version_file):
                with open(version_file, 'r') as f:
                    for line in f:
                        if line.startswith('__version__'):
                            return line.split('=')[1].strip().strip('"\'')
                            
            # Если не удалось, возвращаем заглушку
            return '1.0.0'
            
        except Exception:
            return '1.0.0'
            
    def get_update_status(self) -> Dict:
        """Получить статус обновления"""
        return {
            'enabled': self.config.get('enabled', True),
            'is_running': self.is_running,
            'current_version': self.current_version,
            'latest_version': self.latest_version,
            'update_available': self.update_available,
            'is_downloading': self.is_downloading,
            'download_progress': self.download_progress,
            'is_installing': self.is_installing
        }
        
    def get_update_info(self) -> Optional[Dict]:
        """Получить информацию об обновлении"""
        return self.update_info
        
    def cancel_download(self):
        """Отменить скачивание"""
        self.is_downloading = False
        if self.downloader_thread and self.downloader_thread.is_alive():
            # Прервать поток скачивания
            self.downloader_thread.join(timeout=1)
            
    def skip_update(self, version: str):
        """Пропустить обновление до указанной версии"""
        try:
            skipped_updates_file = 'skipped_updates.json'
            skipped = []
            
            if os.path.exists(skipped_updates_file):
                with open(skipped_updates_file, 'r') as f:
                    skipped = json.load(f)
                    
            if version not in skipped:
                skipped.append(version)
                
                with open(skipped_updates_file, 'w') as f:
                    json.dump(skipped, f)
                    
            self.logger.info(f"Обновление до версии {version} пропущено")
            
        except Exception as e:
            self.logger.error(f"Ошибка пропуска обновления: {e}")

def create_auto_updater(mouseai_instance=None) -> AutoUpdater:
    """Создать автоматический обновлятор"""
    return AutoUpdater(mouseai_instance)