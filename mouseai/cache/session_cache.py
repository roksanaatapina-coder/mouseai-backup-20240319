#!/usr/bin/env python3
"""
Session Cache Module
Система кэширования AI анализов и данных сессий
"""

import time
import json
import hashlib
from typing import Dict, Any, Optional, Union


class SessionCache:
    """Система кэширования для MouseAI"""
    
    def __init__(self, max_size: int = 100, ttl: int = 3600):
        """
        Инициализация кэша
        
        Args:
            max_size: Максимальное количество записей в кэше
            ttl: Время жизни кэша в секундах (3600 = 1 час)
        """
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.max_size = max_size
        self.ttl = ttl  # Time to live in seconds
    
    def get(self, key: str) -> Optional[Any]:
        """Получение данных из кэша"""
        if key in self.cache:
            cached_data = self.cache[key]
            current_time = time.time()
            
            # Проверка времени жизни
            if current_time - cached_data['timestamp'] < self.ttl:
                return cached_data['data']
            else:
                # Удаляем просроченные данные
                del self.cache[key]
                return None
        return None
    
    def set(self, key: str, data: Any) -> None:
        """Сохранение данных в кэш"""
        # Проверка размера кэша
        if len(self.cache) >= self.max_size:
            # Удаляем самую старую запись
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k]['timestamp'])
            del self.cache[oldest_key]
        
        self.cache[key] = {
            'data': data,
            'timestamp': time.time()
        }
    
    def clear(self) -> None:
        """Очистка кэша"""
        self.cache.clear()
    
    def delete(self, key: str) -> bool:
        """Удаление конкретной записи из кэша"""
        if key in self.cache:
            del self.cache[key]
            return True
        return False
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Информация о состоянии кэша"""
        current_time = time.time()
        valid_entries = sum(1 for entry in self.cache.values() 
                          if current_time - entry['timestamp'] < self.ttl)
        
        return {
            'size': len(self.cache),
            'valid_entries': valid_entries,
            'max_size': self.max_size,
            'ttl': self.ttl,
            'usage_percent': (len(self.cache) / self.max_size) * 100 if self.max_size > 0 else 0
        }
    
    def cleanup_expired(self) -> int:
        """Очистка просроченных записей"""
        current_time = time.time()
        expired_keys = [
            key for key, entry in self.cache.items()
            if current_time - entry['timestamp'] >= self.ttl
        ]
        
        for key in expired_keys:
            del self.cache[key]
        
        return len(expired_keys)
    
    def generate_key(self, data: Union[Dict, str, Any]) -> str:
        """Генерация ключа кэша на основе данных"""
        if isinstance(data, dict):
            # Сортируем словарь для консистентности
            data_str = json.dumps(data, sort_keys=True)
        elif isinstance(data, str):
            data_str = data
        else:
            data_str = str(data)
        
        # Создаем хеш от данных
        return hashlib.md5(data_str.encode()).hexdigest()
    
    def get_cached_analysis(self, session_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Получение кэшированного анализа сессии"""
        cache_key = self.generate_key(session_data)
        return self.get(cache_key)
    
    def cache_analysis(self, session_data: Dict[str, Any], analysis: Dict[str, Any]) -> None:
        """Кэширование анализа сессии"""
        cache_key = self.generate_key(session_data)
        self.set(cache_key, analysis)


# Глобальный экземпляр кэша
session_cache = SessionCache(max_size=50, ttl=1800)  # 30 минут TTL, 50 записей