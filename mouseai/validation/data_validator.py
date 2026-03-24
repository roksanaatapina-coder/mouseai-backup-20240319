#!/usr/bin/env python3
"""
Data Validator Module
Валидация данных сессии и AI ответов
"""

import json
from typing import Dict, Any, Optional


class DataValidator:
    """Система валидации данных для MouseAI"""
    
    @staticmethod
    def validate_session_data(data: Dict[str, Any]) -> bool:
        """Валидация данных сессии"""
        required_fields = ['game', 'duration', 'metrics']
        
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
        
        # Проверка типа и значения duration
        if not isinstance(data['duration'], (int, float)) or data['duration'] <= 0:
            raise ValueError("Invalid duration value - must be positive number")
            
        # Проверка типа и значения game
        if not isinstance(data['game'], str) or not data['game'].strip():
            raise ValueError("Invalid game name - must be non-empty string")
            
        # Проверка metrics
        if not isinstance(data['metrics'], dict):
            raise ValueError("Invalid metrics format - must be dictionary")
            
        return True
    
    @staticmethod
    def validate_ai_response(response: Dict[str, Any]) -> bool:
        """Валидация ответа AI"""
        if not response:
            raise ValueError("Empty AI response")
            
        if 'choices' not in response:
            raise ValueError("Invalid AI response format - missing 'choices' field")
            
        if not response['choices']:
            raise ValueError("Empty AI response choices")
            
        if 'message' not in response['choices'][0]:
            raise ValueError("Invalid AI response format - missing 'message' field")
            
        if 'content' not in response['choices'][0]['message']:
            raise ValueError("Invalid AI response format - missing 'content' field")
            
        return True
    
    @staticmethod
    def validate_metrics(metrics: Dict[str, Any]) -> bool:
        """Валидация метрик сессии"""
        allowed_metrics = [
            'movement_speed', 'click_frequency', 'accuracy', 
            'stability', 'reaction_time', 'tracking_score'
        ]
        
        for metric_name, value in metrics.items():
            if metric_name not in allowed_metrics:
                raise ValueError(f"Unknown metric: {metric_name}")
            
            if not isinstance(value, (int, float)):
                raise ValueError(f"Invalid metric value for {metric_name} - must be number")
                
        return True
    
    @staticmethod
    def sanitize_session_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """Санитизация данных сессии"""
        sanitized = data.copy()
        
        # Очистка названия игры
        if 'game' in sanitized:
            sanitized['game'] = sanitized['game'].strip()
            
        # Округление duration
        if 'duration' in sanitized:
            sanitized['duration'] = round(float(sanitized['duration']), 2)
            
        # Санитизация метрик
        if 'metrics' in sanitized:
            sanitized['metrics'] = {
                k: round(float(v), 2) if isinstance(v, (int, float)) else v
                for k, v in sanitized['metrics'].items()
                if isinstance(v, (int, float, str, bool))
            }
            
        return sanitized