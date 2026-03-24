#!/usr/bin/env python3
"""
Update Manager Module
Система обновления приложения MouseAI
"""

import requests
import json
import os
import sys
import zipfile
import tempfile
import shutil
import logging
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass


@dataclass
class UpdateInfo:
    """Информация об обновлении"""
    version: str
    download_url: str
    changelog: str
    size: int
    checksum: str


class UpdateManager:
    """Менеджер обновлений для MouseAI"""
    
    def __init__(self, current_version: str = "1.0.0"):
        """
        Инициализация менеджера обновлений
        
        Args:
            current_version: Текущая версия приложения
        """
        self.current_version = current_version
        self.update_server = "https://api.mouseai.com/updates"
        self.logger = logging.getLogger(__name__)
        self.update_available_callback: Optional[Callable] = None
        self.download_progress_callback: Optional[Callable] = None
        self.install_progress_callback: Optional[Callable] = None
    
    def check_for_updates(self) -> Optional[UpdateInfo]:
        """Проверка обновлений"""
        try:
            self.logger.info(f"Checking for updates (current version: {self.current_version})")
            
            response = requests.get(
                f"{self.update_server}/check", 
                params={"version": self.current_version},
                timeout=10,
                headers={"User-Agent": "MouseAI-Update-Checker/1.0"}
            )
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("update_available", False):
                update_info = UpdateInfo(
                    version=data["version"],
                    download_url=data["download_url"],
                    changelog=data.get("changelog", ""),
                    size=data.get("size", 0),
                    checksum=data.get("checksum", "")
                )
                
                self.logger.info(f"Update available: {update_info.version}")
                return update_info
            else:
                self.logger.info("No updates available")
                return None
                
        except requests.RequestException as e:
            self.logger.error(f"Update check failed: {e}")
            return None
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid response format: {e}")
            return None
    
    def download_update(self, update_info: UpdateInfo, progress_callback: Optional[Callable] = None) -> Optional[str]:
        """Загрузка обновления"""
        try:
            self.logger.info(f"Downloading update {update_info.version}")
            
            response = requests.get(update_info.download_url, stream=True, timeout=30)
            response.raise_for_status()
            
            # Создаем временный файл для загрузки
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
            temp_filename = temp_file.name
            
            # Получаем размер файла
            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0
            
            with temp_file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        temp_file.write(chunk)
                        downloaded_size += len(chunk)
                        
                        # Вызов callback для отображения прогресса
                        if progress_callback and total_size > 0:
                            progress = (downloaded_size / total_size) * 100
                            progress_callback(progress, downloaded_size, total_size)
            
            self.logger.info(f"Update downloaded to {temp_filename}")
            return temp_filename
            
        except Exception as e:
            self.logger.error(f"Update download failed: {e}")
            return None
    
    def verify_update(self, file_path: str, expected_checksum: str) -> bool:
        """Проверка целостности загруженного обновления"""
        try:
            import hashlib
            
            with open(file_path, 'rb') as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()
            
            if file_hash.lower() == expected_checksum.lower():
                self.logger.info("Update verification successful")
                return True
            else:
                self.logger.error(f"Update verification failed: expected {expected_checksum}, got {file_hash}")
                return False
                
        except Exception as e:
            self.logger.error(f"Update verification error: {e}")
            return False
    
    def extract_update(self, zip_path: str, extract_path: str) -> bool:
        """Извлечение обновления из архива"""
        try:
            self.logger.info(f"Extracting update to {extract_path}")
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)
            
            self.logger.info("Update extraction completed")
            return True
            
        except Exception as e:
            self.logger.error(f"Update extraction failed: {e}")
            return False
    
    def apply_update(self, update_info: UpdateInfo, update_file: str) -> bool:
        """Применение обновления"""
        try:
            self.logger.info(f"Applying update {update_info.version}")
            
            # Проверка целостности
            if update_info.checksum and not self.verify_update(update_file, update_info.checksum):
                self.logger.error("Update verification failed")
                return False
            
            # Создаем временную директорию для извлечения
            temp_dir = tempfile.mkdtemp()
            
            try:
                # Извлечение обновления
                if not self.extract_update(update_file, temp_dir):
                    return False
                
                # Получаем путь к текущему приложению
                app_path = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(__file__)
                
                # Резервное копирование текущей версии
                backup_dir = os.path.join(app_path, f"backup_{self.current_version}")
                if os.path.exists(backup_dir):
                    shutil.rmtree(backup_dir)
                shutil.copytree(app_path, backup_dir, ignore=lambda src, names: ['.git', '__pycache__', '*.pyc'])
                
                # Копирование новых файлов
                for item in os.listdir(temp_dir):
                    src = os.path.join(temp_dir, item)
                    dst = os.path.join(app_path, item)
                    
                    if os.path.isdir(src):
                        if os.path.exists(dst):
                            shutil.rmtree(dst)
                        shutil.copytree(src, dst)
                    else:
                        shutil.copy2(src, dst)
                
                self.logger.info("Update applied successfully")
                return True
                
            finally:
                # Очистка временных файлов
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
                if os.path.exists(update_file):
                    os.unlink(update_file)
                    
        except Exception as e:
            self.logger.error(f"Update application failed: {e}")
            return False
    
    def restart_application(self) -> None:
        """Перезапуск приложения"""
        try:
            self.logger.info("Restarting application")
            python = sys.executable
            os.execl(python, python, *sys.argv)
        except Exception as e:
            self.logger.error(f"Application restart failed: {e}")
    
    def check_and_install_update(self, auto_install: bool = False) -> bool:
        """Проверка и установка обновления (полный цикл)"""
        # Проверка обновлений
        update_info = self.check_for_updates()
        if not update_info:
            return False
        
        # Загрузка обновления
        update_file = self.download_update(update_info, self.download_progress_callback)
        if not update_file:
            return False
        
        # Применение обновления
        if self.apply_update(update_info, update_file):
            if auto_install:
                self.restart_application()
            return True
        
        return False
    
    def set_update_available_callback(self, callback: Callable[[UpdateInfo], None]):
        """Установка callback для уведомления о доступном обновлении"""
        self.update_available_callback = callback
    
    def set_download_progress_callback(self, callback: Callable[[float, int, int], None]):
        """Установка callback для отображения прогресса загрузки"""
        self.download_progress_callback = callback
    
    def set_install_progress_callback(self, callback: Callable[[float], None]):
        """Установка callback для отображения прогресса установки"""
        self.install_progress_callback = callback


# Глобальный экземпляр менеджера обновлений
update_manager = UpdateManager()