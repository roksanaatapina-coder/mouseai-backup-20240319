#!/usr/bin/env python3
"""
Testing Module - Модуль тестирования системы MouseAI

Этот модуль содержит все тесты для системы анализа движений мыши MouseAI.
"""

from .test_runner import TestRunner
from .test_data_collector import TestDataCollector
from .test_analysis import TestScientificMetrics, TestMLModels
from .test_integration import TestDiscordBot, TestTelegramBot, TestOBSOverlay, TestRESTAPI
from .test_ui import TestUI, TestUIThreading, TestUIPerformance
from .test_performance import TestPerformance, TestBenchmark
from .test_comprehensive import TestComprehensive, TestSystemHealth, TestIntegrationScenarios

__all__ = [
    'TestRunner',
    'TestDataCollector',
    'TestScientificMetrics',
    'TestMLModels',
    'TestDiscordBot',
    'TestTelegramBot',
    'TestOBSOverlay',
    'TestRESTAPI',
    'TestUI',
    'TestUIThreading',
    'TestUIPerformance',
    'TestPerformance',
    'TestBenchmark',
    'TestComprehensive',
    'TestSystemHealth',
    'TestIntegrationScenarios'
]

# Версия модуля тестирования
__version__ = '1.0.0'
__author__ = 'MouseAI Team'
__description__ = 'Comprehensive testing suite for MouseAI system'

def run_all_tests():
    """
    Запустить все тесты системы
    
    Returns:
        bool: True если все тесты прошли успешно, False в противном случае
    """
    import unittest
    import sys
    import os
    
    # Добавляем путь к проекту
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
    
    # Создаем тестовый набор
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Добавляем все тесты
    test_modules = [
        'mouseai.testing.test_data_collector',
        'mouseai.testing.test_analysis',
        'mouseai.testing.test_integration',
        'mouseai.testing.test_ui',
        'mouseai.testing.test_performance',
        'mouseai.testing.test_comprehensive'
    ]
    
    for module_name in test_modules:
        try:
            module = __import__(module_name, fromlist=[''])
            tests = loader.loadTestsFromModule(module)
            suite.addTests(tests)
        except ImportError as e:
            print(f"Не удалось загрузить модуль {module_name}: {e}")
            return False
    
    # Запускаем тесты
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Возвращаем результат
    return result.wasSuccessful()

def run_performance_tests():
    """
    Запустить только тесты производительности
    
    Returns:
        bool: True если все тесты производительности прошли успешно, False в противном случае
    """
    import unittest
    import sys
    import os
    
    # Добавляем путь к проекту
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
    
    # Создаем тестовый набор для производительности
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Добавляем тесты производительности
    from .test_performance import TestPerformance, TestBenchmark
    
    suite.addTests(loader.loadTestsFromTestCase(TestPerformance))
    suite.addTests(loader.loadTestsFromTestCase(TestBenchmark))
    
    # Запускаем тесты
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Возвращаем результат
    return result.wasSuccessful()

def run_integration_tests():
    """
    Запустить только интеграционные тесты
    
    Returns:
        bool: True если все интеграционные тесты прошли успешно, False в противном случае
    """
    import unittest
    import sys
    import os
    
    # Добавляем путь к проекту
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
    
    # Создаем тестовый набор для интеграции
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Добавляем интеграционные тесты
    from .test_integration import TestDiscordBot, TestTelegramBot, TestOBSOverlay, TestRESTAPI
    
    suite.addTests(loader.loadTestsFromTestCase(TestDiscordBot))
    suite.addTests(loader.loadTestsFromTestCase(TestTelegramBot))
    suite.addTests(loader.loadTestsFromTestCase(TestOBSOverlay))
    suite.addTests(loader.loadTestsFromTestCase(TestRESTAPI))
    
    # Запускаем тесты
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Возвращаем результат
    return result.wasSuccessful()

def run_ui_tests():
    """
    Запустить только тесты пользовательского интерфейса
    
    Returns:
        bool: True если все тесты UI прошли успешно, False в противном случае
    """
    import unittest
    import sys
    import os
    
    # Добавляем путь к проекту
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
    
    # Создаем тестовый набор для UI
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Добавляем тесты UI
    from .test_ui import TestUI, TestUIThreading, TestUIPerformance
    
    suite.addTests(loader.loadTestsFromTestCase(TestUI))
    suite.addTests(loader.loadTestsFromTestCase(TestUIThreading))
    suite.addTests(loader.loadTestsFromTestCase(TestUIPerformance))
    
    # Запускаем тесты
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Возвращаем результат
    return result.wasSuccessful()

def run_comprehensive_tests():
    """
    Запустить комплексные тесты системы
    
    Returns:
        bool: True если все комплексные тесты прошли успешно, False в противном случае
    """
    import unittest
    import sys
    import os
    
    # Добавляем путь к проекту
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
    
    # Создаем тестовый набор для комплексных тестов
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Добавляем комплексные тесты
    from .test_comprehensive import TestComprehensive, TestSystemHealth, TestIntegrationScenarios
    
    suite.addTests(loader.loadTestsFromTestCase(TestComprehensive))
    suite.addTests(loader.loadTestsFromTestCase(TestSystemHealth))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegrationScenarios))
    
    # Запускаем тесты
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Возвращаем результат
    return result.wasSuccessful()

def get_test_summary():
    """
    Получить сводку по тестам
    
    Returns:
        dict: Сводка по тестам
    """
    summary = {
        'total_tests': 0,
        'passed_tests': 0,
        'failed_tests': 0,
        'skipped_tests': 0,
        'test_modules': []
    }
    
    # Список всех тестовых модулей
    test_modules = [
        'test_data_collector',
        'test_analysis', 
        'test_integration',
        'test_ui',
        'test_performance',
        'test_comprehensive'
    ]
    
    for module_name in test_modules:
        try:
            module = __import__(f'mouseai.testing.{module_name}', fromlist=[''])
            summary['test_modules'].append({
                'name': module_name,
                'description': getattr(module, '__doc__', 'No description'),
                'status': 'loaded'
            })
        except ImportError:
            summary['test_modules'].append({
                'name': module_name,
                'description': 'Failed to load',
                'status': 'failed'
            })
    
    return summary

if __name__ == '__main__':
    # Запуск всех тестов при прямом вызове модуля
    print("Запуск всех тестов MouseAI...")
    success = run_all_tests()
    
    if success:
        print("\n✅ Все тесты прошли успешно!")
        print("Система MouseAI готова к использованию.")
    else:
        print("\n❌ Некоторые тесты не прошли.")
        print("Проверьте систему перед использованием.")
    
    sys.exit(0 if success else 1)