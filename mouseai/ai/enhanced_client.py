#!/usr/bin/env python3
"""
Enhanced AI Client Module
Улучшенный AI клиент с кэшированием и валидацией
"""

import openai
import json
import logging
from typing import Dict, Any, Optional, List
from mouseai.cache.session_cache import session_cache
from mouseai.validation.data_validator import DataValidator


class EnhancedAIClient:
    """Улучшенный AI клиент для MouseAI"""
    
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        """
        Инициализация AI клиента
        
        Args:
            api_key: API ключ для OpenAI
            model: Модель для использования (по умолчанию gpt-4o-mini)
        """
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
        self.cache = session_cache
        self.logger = logging.getLogger(__name__)
    
    def analyze_session(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Улучшенный анализ сессии с кэшированием и валидацией"""
        try:
            # Валидация входных данных
            DataValidator.validate_session_data(session_data)
            sanitized_data = DataValidator.sanitize_session_data(session_data)
            
            # Генерация ключа кэша
            cache_key = self.cache.generate_key(sanitized_data)
            
            # Проверка кэша
            cached_result = self.cache.get_cached_analysis(sanitized_data)
            if cached_result:
                self.logger.info("Using cached AI analysis")
                return cached_result
            
            # Формирование промпта
            prompt = self._create_analysis_prompt(sanitized_data)
            
            # Выполнение AI запроса
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert aim trainer and gaming performance analyst. Provide detailed, actionable recommendations for improving gaming performance."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500,
                response_format={"type": "json_object"}
            )
            
            # Обработка ответа
            result = self._process_response(response)
            
            # Сохранение в кэш
            self.cache.cache_analysis(sanitized_data, result)
            
            self.logger.info("AI analysis completed successfully")
            return result
            
        except Exception as e:
            self.logger.error(f"AI Analysis Error: {e}")
            return self._get_fallback_analysis(session_data)
    
    def generate_training_plan(self, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Генерация персонального плана тренировок"""
        try:
            # Валидация профиля пользователя
            if not user_profile or 'skill_level' not in user_profile:
                raise ValueError("Invalid user profile")
            
            prompt = self._create_training_plan_prompt(user_profile)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional gaming coach. Create personalized training plans based on user profiles."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,
                max_tokens=2000,
                response_format={"type": "json_object"}
            )
            
            return self._process_response(response)
            
        except Exception as e:
            self.logger.error(f"Training plan generation error: {e}")
            return self._get_fallback_training_plan(user_profile)
    
    def _create_analysis_prompt(self, session_data: Dict[str, Any]) -> str:
        """Создание промпта для анализа сессии"""
        return f"""
        Analyze this gaming aim session data and provide detailed recommendations:
        
        Game: {session_data['game']}
        Duration: {session_data['duration']} seconds
        Metrics: {json.dumps(session_data['metrics'], indent=2)}
        
        Please provide analysis in JSON format with the following structure:
        {{
            "analysis": "Detailed performance analysis focusing on strengths and areas for improvement",
            "recommendations": [
                "Specific actionable recommendations for improvement",
                "Focus areas for training",
                "Equipment suggestions if applicable"
            ],
            "exercises": [
                "Targeted exercises to address specific weaknesses",
                "Progressive training drills",
                "Warm-up and cool-down routines"
            ],
            "equipment": "Specific equipment recommendations based on playstyle and metrics",
            "schedule": "Optimal practice schedule recommendations",
            "progress_tracking": "How to measure and track improvement over time"
        }}
        
        Focus on providing practical, actionable advice that will lead to measurable improvement.
        """
    
    def _create_training_plan_prompt(self, user_profile: Dict[str, Any]) -> str:
        """Создание промпта для плана тренировок"""
        return f"""
        Create a personalized training plan based on this user profile:
        
        Skill Level: {user_profile.get('skill_level', 'Unknown')}
        Main Game: {user_profile.get('main_game', 'Unknown')}
        Playtime per day: {user_profile.get('playtime_per_day', 'Unknown')} hours
        Goals: {user_profile.get('goals', 'Unknown')}
        Current metrics: {json.dumps(user_profile.get('current_metrics', {}), indent=2)}
        
        Create a comprehensive training plan in JSON format:
        {{
            "weekly_plan": "Detailed week-by-week training schedule",
            "daily_routine": "Daily training routine breakdown",
            "progression_path": "How to progress from current level to goals",
            "key_focus_areas": ["Main areas to focus on", "Priority skills to develop"],
            "milestones": "Key milestones and how to track them",
            "rest_recommendations": "Rest and recovery recommendations"
        }}
        """
    
    def _process_response(self, response) -> Dict[str, Any]:
        """Обработка ответа от AI"""
        try:
            content = response.choices[0].message.content
            result = json.loads(content)
            
            # Валидация структуры ответа
            required_fields = ['analysis', 'recommendations', 'exercises']
            for field in required_fields:
                if field not in result:
                    result[field] = f"Missing {field} in AI response"
            
            return result
            
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON decode error: {e}")
            return self._get_fallback_analysis({})
        except Exception as e:
            self.logger.error(f"Response processing error: {e}")
            return self._get_fallback_analysis({})
    
    def _get_fallback_analysis(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Резервный анализ при ошибке AI"""
        return {
            "analysis": "Unable to perform detailed AI analysis. Please try again later or check your internet connection.",
            "recommendations": [
                "Continue practicing regularly with focus on consistency",
                "Monitor your progress over time using the built-in tracking",
                "Ensure proper mouse and DPI settings for your playstyle",
                "Take regular breaks to avoid fatigue and maintain performance"
            ],
            "exercises": [
                "Basic aim training with consistent settings",
                "Flick shots to improve reaction time and accuracy",
                "Tracking exercises for smooth mouse movements",
                "Warm-up routines before gaming sessions"
            ],
            "equipment": "Ensure your mouse sensitivity (DPI) and in-game settings are optimized for your playstyle. Consider ergonomic equipment for long sessions.",
            "schedule": "Practice 30-60 minutes daily with proper warm-up and cool-down. Focus on quality over quantity in training sessions.",
            "progress_tracking": "Use the built-in metrics tracking to monitor improvements in accuracy, consistency, and reaction time over time."
        }
    
    def _get_fallback_training_plan(self, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Резервный план тренировок при ошибке"""
        return {
            "weekly_plan": "Start with basic aim training 3-4 times per week, gradually increasing frequency and intensity based on progress.",
            "daily_routine": "15 minutes warm-up, 30-45 minutes focused training, 10 minutes cool-down and review.",
            "progression_path": "Begin with basic exercises, master fundamentals, then progress to advanced techniques and game-specific scenarios.",
            "key_focus_areas": ["Consistency", "Accuracy", "Reaction time", "Muscle memory"],
            "milestones": ["Improved consistency scores", "Better accuracy metrics", "Faster reaction times", "Enhanced muscle memory"],
            "rest_recommendations": "Take at least 1-2 rest days per week. Ensure proper sleep and hydration for optimal performance."
        }
    
    def clear_cache(self) -> None:
        """Очистка кэша"""
        self.cache.clear()
        self.logger.info("AI cache cleared")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Получение статистики кэша"""
        return self.cache.get_cache_info()