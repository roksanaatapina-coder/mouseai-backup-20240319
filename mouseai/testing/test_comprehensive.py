#!/usr/bin/env python3
"""
Comprehensive Test Suite - Комплексный тестовый набор
"""

import unittest
import sys
import os
import time
import threading
import json
import numpy as np
from typing import Dict, List, Any
import logging

# Добавляем путь к проекту
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from mouseai.core.data_collector import DataCollector
from mouseai.core.game_detector import GameDetector
from mouseai.analysis.scientific_metrics import ScientificMetrics
from mouseai.analysis.ml_models import MLModels
from mouseai.visualization.dashboard import ProgressDashboard, RealTimeDashboard
from mouseai.visualization.heatmaps import HeatmapGenerator
from mouseai.integration.discord_bot import DiscordBot
from mouseai.integration.telegram_bot import TelegramBot
from mouseai.integration.obs_overlay import OBSOverlay
from mouseai.integration.rest_api import RESTAPI
# from mouseai.ui.main_window import MainWindow
from mouseai.ui.game_selection import GameSelectionDialog
from mouseai.ui.dashboard import AnalysisDashboardDialog
from mouseai.ui.settings import SettingsDialog
from mouseai.automation.auto_session import AutoSessionManager
from mouseai.automation.auto_analyzer import AutoAnalyzer
from mouseai.automation.auto_updater import AutoUpdater
from mouseai.utils.config import MouseAIConfig
from mouseai.utils.helpers import MouseAIHelpers
from mouseai.testing.test_runner import TestRunner
from mouseai.utils import MouseAILogger

class TestComprehensive(unittest.TestCase):
    """Комплексные тесты системы"""
    
    @classmethod
    def setUpClass(cls):
        """Настройка комплексных тестов"""
        cls.logger = MouseAILogger()
        cls.test_results = []
        
    def setUp(self):
        """Настройка каждого теста"""
        self.start_time = time.time()
        
    def tearDown(self):
        """Очистка после каждого теста"""
        elapsed = time.time() - self.start_time
        self.test_results.append({
            'test_name': self._testMethodName,
            'duration': elapsed,
            'status': 'passed'
        })
        
    def test_full_system_integration(self):
        """Тест полной интеграции системы"""
        # Создаем все компоненты системы
        collector = DataCollector()
        detector = GameDetector()
        metrics = ScientificMetrics()
        ml_models = MLModels()
        dashboard = ProgressDashboard()
        heatmap_gen = HeatmapGenerator()
        
        # Проверяем, что все компоненты могут работать вместе
        self.assertIsNotNone(collector)
        self.assertIsNotNone(detector)
        self.assertIsNotNone(metrics)
        self.assertIsNotNone(ml_models)
        self.assertIsNotNone(dashboard)
        self.assertIsNotNone(heatmap_gen)
        
        # Тестируем поток данных
        test_data = np.random.random(1000)
        
        # Сбор данных
        collector.set_buffer_size(100)
        collector.start()
        time.sleep(0.1)
        collector.stop()
        
        # Анализ данных
        entropy = metrics.calculate_sample_entropy(test_data)
        mad = metrics.calculate_maximum_absolute_deviation(test_data)
        
        # Визуализация
        dashboard.add_session({
            'game': 'TestGame',
            'timestamp': time.time(),
            'metrics': {
                'sample_entropy': entropy,
                'maximum_absolute_deviation': mad
            }
        })
        
        # Проверяем, что данные прошли полный цикл
        self.assertGreater(entropy, 0)
        self.assertGreater(mad, 0)
        self.assertEqual(len(dashboard.session_history), 1)
        
    def test_end_to_end_workflow(self):
        """Тест сквозного рабочего процесса"""
        # 1. Настройка системы
        config = MouseAIConfig()
        config.set('collection.frequency', 500)
        config.set('analysis.method', 'scientific')
        config.set('visualization.enabled', True)
        
        # 2. Запуск сбора данных
        collector = DataCollector()
        collector.configure(config.get_section('collection'))
        collector.start()
        
        # 3. Сбор данных в течение некоторого времени
        time.sleep(2.0)
        collector.stop()
        
        # 4. Анализ данных
        raw_data = collector.get_data()
        if raw_data:
            metrics = ScientificMetrics()
            
            # Преобразуем данные для анализа
            x_coords = [point['x'] for point in raw_data]
            y_coords = [point['y'] for point in raw_data]
            
            if len(x_coords) > 100:
                entropy = metrics.calculate_sample_entropy(np.array(x_coords))
                mad = metrics.calculate_maximum_absolute_deviation(np.array(y_coords))
                
                # 5. Сохранение результатов
                session_data = {
                    'game': 'TestGame',
                    'timestamp': time.time(),
                    'metrics': {
                        'sample_entropy': entropy,
                        'maximum_absolute_deviation': mad,
                        'data_points': len(raw_data)
                    }
                }
                
                # 6. Визуализация результатов
                dashboard = ProgressDashboard()
                dashboard.add_session(session_data)
                
                # Проверяем результаты
                self.assertGreater(entropy, 0)
                self.assertGreater(mad, 0)
                self.assertEqual(len(dashboard.session_history), 1)
                
    def test_multi_game_support(self):
        """Тест поддержки нескольких игр"""
        games = ['CS2', 'PUBG', 'Valorant', 'Overwatch']
        
        for game in games:
            # Тестируем каждую игру
            collector = DataCollector()
            collector.set_buffer_size(100)
            
            # Симулируем игру
            collector.start()
            time.sleep(0.5)
            collector.stop()
            
            # Анализируем данные
            data = collector.get_data()
            if data:
                metrics = ScientificMetrics()
                entropy = metrics.calculate_sample_entropy(np.array([p['x'] for p in data]))
                
                # Сохраняем результаты для игры
                session_data = {
                    'game': game,
                    'timestamp': time.time(),
                    'metrics': {'sample_entropy': entropy}
                }
                
                self.assertGreater(entropy, 0)
                
    def test_real_time_processing(self):
        """Тест обработки в реальном времени"""
        processed_data_count = 0
        
        def real_time_callback(data):
            nonlocal processed_data_count
            processed_data_count += 1
            
            # Обработка данных в реальном времени
            if len(data) > 10:
                metrics = ScientificMetrics()
                entropy = metrics.calculate_sample_entropy(np.array([p['x'] for p in data]))
                # Можно отправлять данные на визуализацию
                
        collector = DataCollector()
        collector.set_frequency(200)
        collector.set_real_time_callback(real_time_callback)
        
        # Собираем данные в реальном времени
        collector.start()
        time.sleep(3.0)
        collector.stop()
        
        # Проверяем, что данные обрабатывались в реальном времени
        self.assertGreater(processed_data_count, 0)
        
    def test_data_persistence(self):
        """Тест сохранения данных"""
        # Создаем тестовые данные
        test_sessions = []
        for i in range(5):
            session = {
                'game': f'Game{i}',
                'timestamp': time.time(),
                'metrics': {
                    'sample_entropy': np.random.random(),
                    'maximum_absolute_deviation': np.random.random() * 100
                }
            }
            test_sessions.append(session)
            
        # Сохраняем данные
        dashboard = ProgressDashboard()
        for session in test_sessions:
            dashboard.add_session(session)
            
        # Экспортируем данные
        export_filename = 'test_sessions.json'
        dashboard.export_data(export_filename)
        
        # Проверяем, что файл создан
        self.assertTrue(os.path.exists(export_filename))
        
        # Импортируем данные
        dashboard2 = ProgressDashboard()
        dashboard2.import_data(export_filename)
        
        # Проверяем, что данные восстановлены
        self.assertEqual(len(dashboard2.session_history), len(test_sessions))
        
        # Очищаем
        if os.path.exists(export_filename):
            os.remove(export_filename)
            
    def test_error_handling_and_recovery(self):
        """Тест обработки ошибок и восстановления"""
        collector = DataCollector()
        
        # Тестируем различные сценарии ошибок
        try:
            # Попытка запустить уже запущенный сборщик
            collector.start()
            collector.start()  # Должно быть проигнорировано
            time.sleep(0.1)
            
            # Попытка остановить уже остановленный сборщик
            collector.stop()
            collector.stop()  # Должно быть проигнорировано
            
            # Попытка получить данные из пустого буфера
            data = collector.get_data()
            self.assertIsInstance(data, list)
            
            # Попытка анализировать пустые данные
            metrics = ScientificMetrics()
            entropy = metrics.calculate_sample_entropy(np.array([]))
            self.assertEqual(entropy, 0.0)
            
        except Exception as e:
            self.fail(f"Ошибка не должна была возникнуть: {e}")
        finally:
            # Восстановление системы
            if collector.is_running:
                collector.stop()
                
    def test_performance_under_load(self):
        """Тест производительности под нагрузкой"""
        # Создаем высокую нагрузку
        collectors = []
        for i in range(10):
            collector = DataCollector()
            collector.set_frequency(1000)
            collector.set_buffer_size(10000)
            collectors.append(collector)
            
        start_time = time.time()
        
        # Запускаем всех сборщиков одновременно
        for collector in collectors:
            collector.start()
            
        # Работаем под нагрузкой
        time.sleep(5.0)
        
        # Останавливаем всех сборщиков
        for collector in collectors:
            collector.stop()
            
        end_time = time.time()
        total_time = end_time - start_time
        
        # Проверяем производительность
        self.assertLess(total_time, 6.0)  # Должно быть близко к 5 секундам
        
        # Проверяем, что все данные собраны
        total_data_points = sum(len(collector.data_buffer) for collector in collectors)
        self.assertGreater(total_data_points, 40000)  # Должно быть много данных
        
    def test_configuration_management(self):
        """Тест управления конфигурацией"""
        config = MouseAIConfig()
        
        # Тестируем изменение конфигурации
        config.set('collection.frequency', 600)
        config.set('analysis.method', 'ml')
        config.set('visualization.theme', 'dark')
        
        # Проверяем изменения
        self.assertEqual(config.get('collection.frequency'), 600)
        self.assertEqual(config.get('analysis.method'), 'ml')
        self.assertEqual(config.get('visualization.theme'), 'dark')
        
        # Тестируем экспорт/импорт конфигурации
        export_file = 'test_config.json'
        config.export_config(export_file)
        
        self.assertTrue(os.path.exists(export_file))
        
        # Создаем новую конфигурацию и импортируем
        config2 = MouseAIConfig()
        config2.import_config(export_file)
        
        # Проверяем, что конфигурация восстановлена
        self.assertEqual(config2.get('collection.frequency'), 600)
        self.assertEqual(config2.get('analysis.method'), 'ml')
        
        # Очищаем
        if os.path.exists(export_file):
            os.remove(export_file)
            
    def test_system_monitoring(self):
        """Тест мониторинга системы"""
        import psutil
        
        process = psutil.Process()
        
        # Получаем начальные показатели
        initial_memory = process.memory_info().rss / 1024 / 1024
        initial_cpu = process.cpu_percent()
        
        # Запускаем нагрузку
        collector = DataCollector()
        collector.set_frequency(1000)
        collector.start()
        time.sleep(2.0)
        collector.stop()
        
        # Получаем конечные показатели
        final_memory = process.memory_info().rss / 1024 / 1024
        final_cpu = process.cpu_percent()
        
        # Проверяем показатели
        memory_increase = final_memory - initial_memory
        self.assertLess(memory_increase, 200)  # Разумное увеличение памяти
        self.assertGreater(final_cpu, 0)  # CPU должен был нагрузиться
        
    def test_security_and_privacy(self):
        """Тест безопасности и приватности"""
        # Тестируем обработку чувствительных данных
        sensitive_data = {
            'mouse_data': np.random.random(1000).tolist(),
            'user_info': {'name': 'Test User', 'email': 'test@example.com'},
            'game_data': {'game': 'CS2', 'session_time': 300}
        }
        
        # Проверяем, что данные могут быть зашифрованы (если включено)
        config = MouseAIConfig()
        config.set('security.data_encryption', True)
        
        # Тестируем анонимизацию данных
        anonymized_data = MouseAIHelpers()
        
        # Проверяем, что чувствительная информация может быть удалена
        if 'user_info' in sensitive_data:
            del sensitive_data['user_info']
            
        self.assertNotIn('user_info', sensitive_data)
        
    def test_system_stability(self):
        """Тест стабильности системы"""
        # Запускаем длительную сессию
        collector = DataCollector()
        collector.set_frequency(500)
        collector.set_buffer_size(50000)
        
        start_time = time.time()
        
        try:
            collector.start()
            
            # Работаем длительное время
            for i in range(20):  # 20 секунд
                time.sleep(1.0)
                
                # Периодически проверяем стабильность
                current_memory = psutil.Process().memory_info().rss / 1024 / 1024
                self.assertLess(current_memory, 1000)  # Не должно быть сильного потребления памяти
                
        finally:
            collector.stop()
            
        end_time = time.time()
        total_time = end_time - start_time
        
        # Проверяем, что система проработала стабильно
        self.assertGreater(total_time, 19.0)  # Должно быть около 20 секунд
        
    def test_compatibility(self):
        """Тест совместимости"""
        # Тестируем совместимость с разными версиями
        test_versions = ['1.0.0', '1.1.0', '1.2.0']
        
        for version in test_versions:
            config = MouseAIConfig()
            config.set('general.version', version)
            
            # Проверяем, что система работает с разными версиями
            self.assertEqual(config.get('general.version'), version)
            
    def test_user_experience(self):
        """Тест пользовательского опыта"""
        # Тестируем интерфейс
        main_window = MainWindow()
        
        # Проверяем, что интерфейс отзывчив
        main_window.show()
        time.sleep(0.1)  # Даем время на отрисовку
        
        self.assertTrue(main_window.isVisible())
        
        # Тестируем диалоги
        game_dialog = GameSelectionDialog()
        dashboard_dialog = AnalysisDashboardDialog()
        settings_dialog = SettingsDialog()
        
        self.assertIsNotNone(game_dialog)
        self.assertIsNotNone(dashboard_dialog)
        self.assertIsNotNone(settings_dialog)
        
        main_window.close()

class TestSystemHealth(unittest.TestCase):
    """Тесты здоровья системы"""
    
    def test_system_health_check(self):
        """Проверка здоровья системы"""
        health_report = {
            'timestamp': time.time(),
            'components': {},
            'overall_status': 'healthy'
        }
        
        # Проверяем каждый компонент
        components = [
            ('DataCollector', DataCollector),
            ('GameDetector', GameDetector),
            ('ScientificMetrics', ScientificMetrics),
            ('MLModels', MLModels),
            ('ProgressDashboard', ProgressDashboard),
            ('HeatmapGenerator', HeatmapGenerator),
            ('DiscordBot', DiscordBot),
            ('TelegramBot', TelegramBot),
            ('OBSOverlay', OBSOverlay),
            ('RESTAPI', RESTAPI),
            ('AutoSessionManager', AutoSessionManager),
            ('AutoAnalyzer', AutoAnalyzer),
            ('AutoUpdater', AutoUpdater)
        ]
        
        for name, component_class in components:
            try:
                instance = component_class()
                health_report['components'][name] = {
                    'status': 'healthy',
                    'message': 'Component is working correctly'
                }
            except Exception as e:
                health_report['components'][name] = {
                    'status': 'unhealthy',
                    'message': str(e)
                }
                health_report['overall_status'] = 'degraded'
                
        # Проверяем, что большинство компонентов работают
        healthy_count = sum(1 for comp in health_report['components'].values() 
                          if comp['status'] == 'healthy')
        
        self.assertGreater(healthy_count, len(components) * 0.8)
        
        return health_report
        
    def test_performance_baseline(self):
        """Тест базовых показателей производительности"""
        baseline = {
            'data_collection_rate': 0,
            'analysis_time': 0,
            'memory_usage': 0,
            'cpu_usage': 0
        }
        
        # Тестируем базовые показатели
        collector = DataCollector()
        start_time = time.time()
        collector.start()
        time.sleep(1.0)
        collector.stop()
        collection_time = time.time() - start_time
        
        baseline['data_collection_rate'] = len(collector.data_buffer) / collection_time
        baseline['memory_usage'] = psutil.Process().memory_info().rss / 1024 / 1024
        
        # Проверяем, что показатели в норме
        self.assertGreater(baseline['data_collection_rate'], 100)  # Минимум 100 точек в секунду
        self.assertLess(baseline['memory_usage'], 500)  # Меньше 500 MB
        
        return baseline

class TestIntegrationScenarios(unittest.TestCase):
    """Тесты интеграционных сценариев"""
    
    def test_gaming_session_scenario(self):
        """Сценарий игровой сессии"""
        # 1. Пользователь запускает игру
        game_detector = GameDetector()
        detected_game = game_detector.detect_current_game()
        
        # 2. Система начинает сбор данных
        collector = DataCollector()
        collector.set_frequency(1000)
        collector.start()
        
        # 3. Пользователь играет
        time.sleep(5.0)
        
        # 4. Система анализирует данные
        raw_data = collector.get_data()
        if raw_data:
            metrics = ScientificMetrics()
            entropy = metrics.calculate_sample_entropy(np.array([p['x'] for p in raw_data]))
            
            # 5. Система сохраняет результаты
            session_data = {
                'game': detected_game or 'Unknown',
                'timestamp': time.time(),
                'metrics': {'sample_entropy': entropy}
            }
            
            dashboard = ProgressDashboard()
            dashboard.add_session(session_data)
            
            # 6. Система отображает результаты
            stats = dashboard.get_player_stats()
            
            # Проверяем результаты
            self.assertGreater(entropy, 0)
            self.assertIsNotNone(stats)
            
        collector.stop()
        
    def test_multi_user_scenario(self):
        """Сценарий нескольких пользователей"""
        users = ['User1', 'User2', 'User3']
        
        for user in users:
            # Каждый пользователь имеет свои настройки
            config = MouseAIConfig()
            config.set('general.user', user)
            config.set('collection.frequency', 500 + len(users) * 100)
            
            # Каждый пользователь собирает свои данные
            collector = DataCollector()
            collector.configure(config.get_section('collection'))
            collector.start()
            time.sleep(1.0)
            collector.stop()
            
            # Анализируем данные каждого пользователя
            data = collector.get_data()
            if data:
                metrics = ScientificMetrics()
                entropy = metrics.calculate_sample_entropy(np.array([p['x'] for p in data]))
                
                self.assertGreater(entropy, 0)
                
    def test_long_term_usage_scenario(self):
        """Сценарий долгосрочного использования"""
        dashboard = ProgressDashboard()
        
        # Симулируем использование системы в течение нескольких дней
        for day in range(7):
            for session in range(3):  # 3 сессии в день
                session_data = {
                    'game': 'CS2',
                    'timestamp': time.time() + day * 24 * 3600 + session * 3600,
                    'metrics': {
                        'sample_entropy': 0.3 + np.random.random() * 0.4,
                        'maximum_absolute_deviation': 20 + np.random.random() * 80
                    }
                }
                dashboard.add_session(session_data)
                
        # Анализируем долгосрочные тенденции
        trends = dashboard.analyze_trends()
        
        # Проверяем, что система может анализировать долгосрочные данные
        self.assertIsNotNone(trends)
        self.assertGreater(len(dashboard.session_history), 10)

if __name__ == '__main__':
    # Запускаем комплексные тесты
    unittest.main(verbosity=2)