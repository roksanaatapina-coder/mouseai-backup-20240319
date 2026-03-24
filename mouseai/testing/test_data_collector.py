#!/usr/bin/env python3
"""
Test Data Collector - Тесты для сборщика данных
"""

import unittest
import sys
import os
import time
import threading
from unittest.mock import Mock, patch, MagicMock
import numpy as np

# Добавляем путь к проекту
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from mouseai.core.data_collector import DataCollector
from mouseai.utils import MouseAILogger

class TestDataCollector(unittest.TestCase):
    """Тесты для DataCollector"""
    
    def setUp(self):
        """Настройка теста"""
        self.logger = MouseAILogger()
        self.data_collector = DataCollector()
        
    def tearDown(self):
        """Очистка после теста"""
        if self.data_collector.is_running:
            self.data_collector.stop()
            
    def test_initialization(self):
        """Тест инициализации"""
        self.assertIsNotNone(self.data_collector)
        self.assertFalse(self.data_collector.is_running)
        self.assertEqual(len(self.data_collector.data_buffer), 0)
        self.assertEqual(self.data_collector.buffer_size, 1000)
        
    def test_start_collection(self):
        """Тест запуска сбора данных"""
        self.data_collector.start()
        self.assertTrue(self.data_collector.is_running)
        
        # Даем время на запуск
        time.sleep(0.1)
        
        self.data_collector.stop()
        self.assertFalse(self.data_collector.is_running)
        
    def test_stop_collection(self):
        """Тест остановки сбора данных"""
        self.data_collector.start()
        self.assertTrue(self.data_collector.is_running)
        
        self.data_collector.stop()
        self.assertFalse(self.data_collector.is_running)
        
    def test_data_collection(self):
        """Тест сбора данных"""
        self.data_collector.start()
        
        # Ждем сбора данных
        time.sleep(0.5)
        
        # Проверяем, что данные собираются
        data_count = len(self.data_collector.data_buffer)
        self.assertGreater(data_count, 0)
        
        self.data_collector.stop()
        
    def test_buffer_size_limit(self):
        """Тест ограничения размера буфера"""
        self.data_collector.buffer_size = 10
        
        self.data_collector.start()
        
        # Ждем, пока буфер не заполнится
        while len(self.data_collector.data_buffer) < 10:
            time.sleep(0.01)
            
        # Проверяем, что буфер не превышает лимит
        self.assertLessEqual(len(self.data_collector.data_buffer), 10)
        
        self.data_collector.stop()
        
    def test_clear_buffer(self):
        """Тест очистки буфера"""
        self.data_collector.start()
        
        # Собираем немного данных
        time.sleep(0.1)
        
        initial_count = len(self.data_collector.data_buffer)
        self.assertGreater(initial_count, 0)
        
        # Очищаем буфер
        self.data_collector.clear_buffer()
        self.assertEqual(len(self.data_collector.data_buffer), 0)
        
        self.data_collector.stop()
        
    def test_get_data(self):
        """Тест получения данных"""
        self.data_collector.start()
        
        # Собираем данные
        time.sleep(0.1)
        
        data = self.data_collector.get_data()
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        
        # Проверяем структуру данных
        if data:
            sample = data[0]
            self.assertIn('x', sample)
            self.assertIn('y', sample)
            self.assertIn('timestamp', sample)
            
        self.data_collector.stop()
        
    def test_get_statistics(self):
        """Тест получения статистики"""
        self.data_collector.start()
        
        # Собираем данные
        time.sleep(0.1)
        
        stats = self.data_collector.get_statistics()
        self.assertIsInstance(stats, dict)
        self.assertIn('data_points', stats)
        self.assertIn('buffer_size', stats)
        self.assertIn('collection_time', stats)
        
        self.data_collector.stop()
        
    def test_pause_resume(self):
        """Тест паузы и возобновления"""
        self.data_collector.start()
        
        # Собираем данные
        time.sleep(0.1)
        initial_count = len(self.data_collector.data_buffer)
        
        # Делаем паузу
        self.data_collector.pause()
        self.assertTrue(self.data_collector.is_paused)
        
        # Ждем
        time.sleep(0.1)
        
        # Возобновляем
        self.data_collector.resume()
        self.assertFalse(self.data_collector.is_paused)
        
        # Собираем больше данных
        time.sleep(0.1)
        final_count = len(self.data_collector.data_buffer)
        
        self.assertGreater(final_count, initial_count)
        
        self.data_collector.stop()
        
    def test_set_frequency(self):
        """Тест установки частоты"""
        initial_frequency = self.data_collector.frequency
        
        # Устанавливаем новую частоту
        new_frequency = 200
        self.data_collector.set_frequency(new_frequency)
        
        # Проверяем, что частота изменилась
        self.assertEqual(self.data_collector.frequency, new_frequency)
        
        # Возвращаем исходную частоту
        self.data_collector.set_frequency(initial_frequency)
        self.assertEqual(self.data_collector.frequency, initial_frequency)
        
    def test_set_buffer_size(self):
        """Тест установки размера буфера"""
        initial_size = self.data_collector.buffer_size
        
        # Устанавливаем новый размер
        new_size = 2000
        self.data_collector.set_buffer_size(new_size)
        
        # Проверяем, что размер изменился
        self.assertEqual(self.data_collector.buffer_size, new_size)
        
        # Возвращаем исходный размер
        self.data_collector.set_buffer_size(initial_size)
        self.assertEqual(self.data_collector.buffer_size, initial_size)
        
    def test_data_validation(self):
        """Тест валидации данных"""
        # Тестируем валидные данные
        valid_data = {'x': 100, 'y': 200, 'timestamp': time.time()}
        self.assertTrue(self.data_collector._validate_data(valid_data))
        
        # Тестируем невалидные данные
        invalid_data = {'x': 'invalid', 'y': 200, 'timestamp': time.time()}
        self.assertFalse(self.data_collector._validate_data(invalid_data))
        
        invalid_data = {'x': 100, 'y': 200}
        self.assertFalse(self.data_collector._validate_data(invalid_data))
        
    def test_noise_filtering(self):
        """Тест фильтрации шума"""
        # Создаем данные с шумом
        noisy_data = [
            {'x': 100, 'y': 200, 'timestamp': time.time()},
            {'x': 101, 'y': 201, 'timestamp': time.time()},
            {'x': 10000, 'y': 20000, 'timestamp': time.time()},  # Шум
            {'x': 102, 'y': 202, 'timestamp': time.time()},
        ]
        
        # Фильтруем шум
        filtered = self.data_collector._filter_noise(noisy_data)
        
        # Проверяем, что шум был отфильтрован
        self.assertLess(len(filtered), len(noisy_data))
        
    def test_data_smoothing(self):
        """Тест сглаживания данных"""
        # Создаем данные для сглаживания
        raw_data = [
            {'x': 100, 'y': 200, 'timestamp': time.time()},
            {'x': 105, 'y': 205, 'timestamp': time.time()},
            {'x': 110, 'y': 210, 'timestamp': time.time()},
        ]
        
        # Сглаживаем данные
        smoothed = self.data_collector._smooth_data(raw_data)
        
        # Проверяем, что данные были сглажены
        self.assertEqual(len(smoothed), len(raw_data))
        
    def test_real_time_processing(self):
        """Тест обработки в реальном времени"""
        processed_data = []
        
        def mock_callback(data):
            processed_data.append(data)
            
        self.data_collector.set_real_time_callback(mock_callback)
        
        self.data_collector.start()
        
        # Собираем данные
        time.sleep(0.2)
        
        self.data_collector.stop()
        
        # Проверяем, что данные были обработаны
        self.assertGreater(len(processed_data), 0)
        
    def test_multiple_callbacks(self):
        """Тест нескольких коллбэков"""
        callback1_data = []
        callback2_data = []
        
        def callback1(data):
            callback1_data.append(data)
            
        def callback2(data):
            callback2_data.append(data)
            
        self.data_collector.add_callback(callback1)
        self.data_collector.add_callback(callback2)
        
        self.data_collector.start()
        
        # Собираем данные
        time.sleep(0.1)
        
        self.data_collector.stop()
        
        # Проверяем, что оба коллбэка сработали
        self.assertGreater(len(callback1_data), 0)
        self.assertGreater(len(callback2_data), 0)
        
    def test_remove_callback(self):
        """Тест удаления коллбэка"""
        callback_data = []
        
        def callback(data):
            callback_data.append(data)
            
        callback_id = self.data_collector.add_callback(callback)
        
        self.data_collector.start()
        
        # Собираем данные
        time.sleep(0.1)
        
        initial_count = len(callback_data)
        
        # Удаляем коллбэк
        self.data_collector.remove_callback(callback_id)
        
        # Собираем больше данных
        time.sleep(0.1)
        
        # Проверяем, что коллбэк больше не вызывается
        self.assertEqual(len(callback_data), initial_count)
        
        self.data_collector.stop()
        
    def test_error_handling(self):
        """Тест обработки ошибок"""
        # Тестируем ошибку при запуске
        with patch.object(self.data_collector, '_collect_data', side_effect=Exception("Test error")):
            try:
                self.data_collector.start()
                time.sleep(0.1)
            except:
                pass
                
        # Проверяем, что система не сломалась
        self.assertFalse(self.data_collector.is_running)
        
    def test_performance(self):
        """Тест производительности"""
        self.data_collector.start()
        
        start_time = time.time()
        
        # Собираем данные в течение 1 секунды
        time.sleep(1.0)
        
        end_time = time.time()
        collection_time = end_time - start_time
        
        data_count = len(self.data_collector.data_buffer)
        
        self.data_collector.stop()
        
        # Проверяем, что данные собирались с приемлемой производительностью
        self.assertGreater(data_count, 0)
        self.assertLess(collection_time, 1.5)  # Должно быть близко к 1 секунде
        
    def test_memory_usage(self):
        """Тест использования памяти"""
        import psutil
        import gc
        
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        self.data_collector.start()
        
        # Собираем много данных
        time.sleep(2.0)
        
        self.data_collector.stop()
        
        # Принудительная сборка мусора
        gc.collect()
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Проверяем, что память не утекает сильно
        self.assertLess(memory_increase, 50)  # Меньше 50 MB
        
    def test_thread_safety(self):
        """Тест потокобезопасности"""
        data_count = []
        
        def collect_data():
            for _ in range(100):
                time.sleep(0.001)
                count = len(self.data_collector.data_buffer)
                data_count.append(count)
                
        self.data_collector.start()
        
        # Запускаем несколько потоков
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=collect_data)
            threads.append(thread)
            thread.start()
            
        # Ждем завершения потоков
        for thread in threads:
            thread.join()
            
        self.data_collector.stop()
        
        # Проверяем, что данные не повреждены
        self.assertGreater(len(data_count), 0)
        self.assertEqual(len(set(data_count)), len(data_count))  # Все значения должны быть уникальными
        
    def test_configuration(self):
        """Тест конфигурации"""
        config = {
            'frequency': 200,
            'buffer_size': 2000,
            'noise_filter': True,
            'smoothing': True
        }
        
        self.data_collector.configure(config)
        
        # Проверяем, что конфигурация применилась
        self.assertEqual(self.data_collector.frequency, 200)
        self.assertEqual(self.data_collector.buffer_size, 2000)
        
    def test_export_data(self):
        """Тест экспорта данных"""
        self.data_collector.start()
        
        # Собираем данные
        time.sleep(0.1)
        
        self.data_collector.stop()
        
        # Экспортируем данные
        filename = 'test_export.json'
        result = self.data_collector.export_data(filename)
        
        # Проверяем, что экспорт прошел успешно
        self.assertTrue(result)
        self.assertTrue(os.path.exists(filename))
        
        # Очищаем
        if os.path.exists(filename):
            os.remove(filename)

if __name__ == '__main__':
    unittest.main()