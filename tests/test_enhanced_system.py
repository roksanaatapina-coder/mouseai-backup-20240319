#!/usr/bin/env python3
"""
Enhanced System Tests Module
Комплексное тестирование улучшенной системы MouseAI
"""

import unittest
import tempfile
import os
import sys
import time
from unittest.mock import Mock, patch, MagicMock

# Добавляем путь к модулям
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from mouseai.validation.data_validator import DataValidator
from mouseai.cache.session_cache import SessionCache, session_cache
from mouseai.ai.enhanced_client import EnhancedAIClient
from mouseai.update.manager import UpdateManager, UpdateInfo
from mouseai.security.anti_ban_system import AntiBanSystem
from mouseai.ui.enhanced_recommendations import EnhancedRecommendationsPanel


class TestDataValidator(unittest.TestCase):
    """Тестирование системы валидации данных"""
    
    def setUp(self):
        self.validator = DataValidator()
    
    def test_valid_session_data(self):
        """Тестирование валидации корректных данных сессии"""
        valid_data = {
            'game': 'CS2',
            'duration': 300,
            'metrics': {'speed': 100, 'accuracy': 85}
        }
        
        result = self.validator.validate_session_data(valid_data)
        self.assertTrue(result)
    
    def test_invalid_session_data_missing_fields(self):
        """Тестирование валидации данных сессии с отсутствующими полями"""
        invalid_data = {
            'game': 'CS2',
            'duration': 300
            # Отсутствует metrics
        }
        
        with self.assertRaises(ValueError) as context:
            self.validator.validate_session_data(invalid_data)
        
        self.assertIn("Missing required field", str(context.exception))
    
    def test_invalid_duration(self):
        """Тестирование валидации недопустимого duration"""
        invalid_data = {
            'game': 'CS2',
            'duration': -100,  # Отрицательное значение
            'metrics': {'speed': 100, 'accuracy': 85}
        }
        
        with self.assertRaises(ValueError) as context:
            self.validator.validate_session_data(invalid_data)
        
        self.assertIn("Invalid duration value", str(context.exception))
    
    def test_invalid_game_name(self):
        """Тестирование валидации недопустимого названия игры"""
        invalid_data = {
            'game': '',  # Пустое название
            'duration': 300,
            'metrics': {'speed': 100, 'accuracy': 85}
        }
        
        with self.assertRaises(ValueError) as context:
            self.validator.validate_session_data(invalid_data)
        
        self.assertIn("Invalid game name", str(context.exception))
    
    def test_sanitize_session_data(self):
        """Тестирование санитизации данных сессии"""
        dirty_data = {
            'game': '  CS2  ',
            'duration': 300.123456,
            'metrics': {
                'speed': 100.5678,
                'accuracy': 85.1234,
                'invalid_field': 'should_be_removed'
            }
        }
        
        sanitized = self.validator.sanitize_session_data(dirty_data)
        
        self.assertEqual(sanitized['game'], 'CS2')
        self.assertEqual(sanitized['duration'], 300.12)
        self.assertEqual(sanitized['metrics']['speed'], 100.57)
        self.assertEqual(sanitized['metrics']['accuracy'], 85.12)
        self.assertNotIn('invalid_field', sanitized['metrics'])


class TestSessionCache(unittest.TestCase):
    """Тестирование системы кэширования"""
    
    def setUp(self):
        self.cache = SessionCache(max_size=3, ttl=1)  # Короткий TTL для тестов
    
    def test_set_and_get(self):
        """Тестирование установки и получения данных"""
        test_data = {'key': 'value', 'number': 42}
        cache_key = 'test_key'
        
        self.cache.set(cache_key, test_data)
        retrieved_data = self.cache.get(cache_key)
        
        self.assertEqual(retrieved_data, test_data)
    
    def test_cache_expiration(self):
        """Тестирование истечения срока действия кэша"""
        test_data = {'data': 'test'}
        cache_key = 'expiring_key'
        
        self.cache.set(cache_key, test_data)
        retrieved_data = self.cache.get(cache_key)
        self.assertEqual(retrieved_data, test_data)
        
        # Ждем истечения TTL
        time.sleep(1.1)
        
        expired_data = self.cache.get(cache_key)
        self.assertIsNone(expired_data)
    
    def test_cache_size_limit(self):
        """Тестирование ограничения размера кэша"""
        # Заполняем кэш до предела
        for i in range(5):  # Больше, чем max_size=3
            self.cache.set(f'key_{i}', {'value': i})
        
        # Проверяем, что кэш не превышает максимальный размер
        cache_info = self.cache.get_cache_info()
        self.assertLessEqual(cache_info['size'], 3)
    
    def test_cache_cleanup(self):
        """Тестирование очистки просроченных записей"""
        # Создаем просроченные записи
        old_time = time.time() - 10  # 10 секунд назад
        self.cache.cache['old_key'] = {'data': 'old', 'timestamp': old_time}
        self.cache.cache['new_key'] = {'data': 'new', 'timestamp': time.time()}
        
        cleaned_count = self.cache.cleanup_expired()
        self.assertEqual(cleaned_count, 1)
        self.assertEqual(len(self.cache.cache), 1)
        self.assertIn('new_key', self.cache.cache)


class TestEnhancedAIClient(unittest.TestCase):
    """Тестирование улучшенного AI клиента"""
    
    def setUp(self):
        self.mock_openai = Mock()
        self.mock_client = Mock()
        self.mock_openai.OpenAI.return_value = self.mock_client
        
        # Мокаем openai в модуле
        with patch.dict('sys.modules', {'openai': self.mock_openai}):
            self.ai_client = EnhancedAIClient(api_key="test_key", model="gpt-4o-mini")
    
    def test_analyze_session_success(self):
        """Тестирование успешного анализа сессии"""
        # Настраиваем мок
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '{"analysis": "test analysis", "recommendations": ["test"]}'

        self.mock_client.chat.completions.create.return_value = mock_response
        
        session_data = {
            'game': 'CS2',
            'duration': 300,
            'metrics': {'speed': 100, 'accuracy': 85}
        }
        
        result = self.ai_client.analyze_session(session_data)
        
        self.assertIn('analysis', result)
        self.assertIn('recommendations', result)
        self.assertEqual(result['analysis'], 'test analysis')
    
    def test_analyze_session_validation_error(self):
        """Тестирование анализа сессии с ошибкой валидации"""
        invalid_data = {'game': 'CS2'}  # Отсутствует duration и metrics
        
        result = self.ai_client.analyze_session(invalid_data)
        
        # Должен вернуться fallback анализ
        self.assertIn('analysis', result)
        self.assertIn('Unable to perform detailed AI analysis', result['analysis'])
    
    def test_cache_functionality(self):
        """Тестирование функциональности кэширования"""
        session_data = {
            'game': 'CS2',
            'duration': 300,
            'metrics': {'speed': 100, 'accuracy': 85}
        }
        
        # Первый вызов - должен использовать AI
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '{"analysis": "test", "recommendations": ["test"]}'
        self.mock_client.chat.completions.create.return_value = mock_response
        
        result1 = self.ai_client.analyze_session(session_data)
        self.assertEqual(result1['analysis'], 'test')
        
        # Второй вызов - должен использовать кэш
        result2 = self.ai_client.analyze_session(session_data)
        self.assertEqual(result2['analysis'], 'test')
        
        # Проверяем, что AI вызывался только один раз
        self.mock_client.chat.completions.create.assert_called_once()


class TestUpdateManager(unittest.TestCase):
    """Тестирование менеджера обновлений"""
    
    def setUp(self):
        self.update_manager = UpdateManager(current_version="1.0.0")
    
    @patch('requests.get')
    def test_check_for_updates_available(self, mock_get):
        """Тестирование проверки обновлений (обновление доступно)"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "update_available": True,
            "version": "1.1.0",
            "download_url": "https://example.com/update.zip",
            "changelog": "New features",
            "size": 1024,
            "checksum": "abc123"
        }
        mock_get.return_value = mock_response
        
        update_info = self.update_manager.check_for_updates()
        
        self.assertIsNotNone(update_info)
        self.assertEqual(update_info.version, "1.1.0")
        self.assertEqual(update_info.download_url, "https://example.com/update.zip")
    
    @patch('requests.get')
    def test_check_for_updates_not_available(self, mock_get):
        """Тестирование проверки обновлений (обновление не доступно)"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"update_available": False}
        mock_get.return_value = mock_response
        
        update_info = self.update_manager.check_for_updates()
        
        self.assertIsNone(update_info)
    
    @patch('requests.get')
    def test_check_for_updates_network_error(self, mock_get):
        """Тестирование проверки обновлений при сетевой ошибке"""
        mock_get.side_effect = Exception("Network error")
        
        update_info = self.update_manager.check_for_updates()
        
        self.assertIsNone(update_info)


class TestAntiBanSystem(unittest.TestCase):
    """Тестирование системы защиты от бана"""
    
    def setUp(self):
        self.anti_ban = AntiBanSystem()
        self.anti_ban.start_protection()
    
    def tearDown(self):
        self.anti_ban.stop_protection()
    
    def test_session_safety_validation(self):
        """Тестирование проверки безопасности сессии"""
        session_data = {
            'game': 'CS2',
            'duration': 300,
            'metrics': {
                'movement_speed': 500,
                'click_frequency': 10,
                'accuracy': 85,
                'stability': 75
            }
        }
        
        result = self.anti_ban.validate_session_safety(session_data)
        
        self.assertIsInstance(result, dict)
        self.assertIn('safe', result)
        self.assertIn('safety_score', result)
        self.assertIn('warnings', result)
        self.assertIn('recommendations', result)
    
    def test_suspicious_session_detection(self):
        """Тестирование обнаружения подозрительной сессии"""
        session_data = {
            'game': 'CS2',
            'duration': 300,
            'metrics': {
                'movement_speed': 3000,  # Очень высокая скорость
                'click_frequency': 50,   # Очень высокая частота кликов
                'accuracy': 99,          # Идеальная точность
                'stability': 99          # Идеальная стабильность
            }
        }
        
        result = self.anti_ban.validate_session_safety(session_data)
        
        # Должны быть предупреждения о подозрительной активности
        self.assertGreater(len(result['warnings']), 0)
        self.assertLess(result['safety_score'], 0.8)  # Низкий уровень безопасности
    
    def test_behavioral_randomization(self):
        """Тестирование behavioral randomization"""
        original_x, original_y = 100.0, 200.0
        base_delay = 0.01
        
        jittered_x, jittered_y, randomized_delay = self.anti_ban.apply_behavioral_randomization(
            original_x, original_y, base_delay
        )
        
        # Координаты должны быть изменены (но не сильно)
        self.assertNotEqual((original_x, original_y), (jittered_x, jittered_y))
        self.assertLess(abs(jittered_x - original_x), 10)  # Ограниченное изменение
        self.assertLess(abs(jittered_y - original_y), 10)
        
        # Задержка должна быть изменена
        self.assertNotEqual(base_delay, randomized_delay)


class TestEnhancedRecommendationsPanel(unittest.TestCase):
    """Тестирование интеллектуальной панели рекомендаций"""
    
    def setUp(self):
        self.recommendations_panel = EnhancedRecommendationsPanel()
    
    def test_update_recommendations(self):
        """Тестирование обновления рекомендаций"""
        # Создаем mock AI клиента
        mock_ai_client = Mock()
        mock_analysis = {
            'analysis': 'Test analysis',
            'recommendations': ['Recommendation 1', 'Recommendation 2'],
            'exercises': ['Exercise 1', 'Exercise 2'],
            'equipment': 'Test equipment',
            'schedule': 'Test schedule',
            'progress_tracking': 'Test progress'
        }
        mock_ai_client.analyze_session.return_value = mock_analysis
        
        self.recommendations_panel.set_ai_client(mock_ai_client)
        
        session_data = {
            'game': 'CS2',
            'duration': 300,
            'metrics': {'speed': 100, 'accuracy': 85}
        }
        
        # Обновляем рекомендации
        self.recommendations_panel.update_recommendations(session_data)
        
        # Проверяем, что данные отображаются
        self.assertEqual(self.recommendations_panel.analysis_text.toPlainText(), 'Test analysis')
        self.assertIn('Recommendation 1', self.recommendations_panel.recommendations_text.toPlainText())
        self.assertIn('Exercise 1', self.recommendations_panel.exercises_text.toPlainText())
        self.assertEqual(self.recommendations_panel.equipment_text.toPlainText(), 'Test equipment')


class TestIntegration(unittest.TestCase):
    """Интеграционные тесты"""
    
    def test_full_workflow(self):
        """Тестирование полного рабочего процесса"""
        # Создаем все компоненты
        validator = DataValidator()
        cache = SessionCache(max_size=10, ttl=3600)
        mock_openai = Mock()
        mock_client = Mock()
        mock_openai.OpenAI.return_value = mock_client
        
        with patch.dict('sys.modules', {'openai': mock_openai}):
            ai_client = EnhancedAIClient(api_key="test_key")
        
        anti_ban = AntiBanSystem()
        recommendations_panel = EnhancedRecommendationsPanel(ai_client)
        
        # Тестовые данные
        session_data = {
            'game': 'CS2',
            'duration': 300,
            'metrics': {'speed': 100, 'accuracy': 85, 'stability': 75}
        }
        
        # Валидация данных
        validator.validate_session_data(session_data)
        sanitized_data = validator.sanitize_session_data(session_data)
        
        # Проверка безопасности
        safety_result = anti_ban.validate_session_safety(sanitized_data)
        self.assertTrue(safety_result['safe'])
        
        # Кэширование (проверяем, что кэш работает)
        cache_key = cache.generate_key(sanitized_data)
        cache.set(cache_key, sanitized_data)
        cached_data = cache.get(cache_key)
        self.assertEqual(cached_data, sanitized_data)
        
        # Обновление рекомендаций
        recommendations_panel.set_ai_client(ai_client)
        recommendations_panel.update_recommendations(sanitized_data)
        
        # Проверяем, что рекомендации обновились
        current_analysis = recommendations_panel.get_current_analysis()
        self.assertIsNotNone(current_analysis)


if __name__ == '__main__':
    # Запуск тестов
    unittest.main(verbosity=2)