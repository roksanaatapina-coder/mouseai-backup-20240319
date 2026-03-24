#!/usr/bin/env python3
"""
Test Performance - Тесты производительности системы
"""

import unittest
import sys
import os
import time
import threading
import psutil
import gc
import numpy as np
from typing import Dict, List, Any
import logging

# Добавляем путь к проекту
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from mouseai.core.data_collector import DataCollector
from mouseai.analysis.scientific_metrics import ScientificMetrics
from mouseai.analysis.ml_models import MLModels
from mouseai.utils import MouseAILogger

class TestPerformance(unittest.TestCase):
    """Тесты производительности системы"""
    
    def setUp(self):
        """Настройка теста"""
        self.logger = MouseAILogger()
        self.process = psutil.Process()
        
    def get_memory_usage(self) -> float:
        """Получить текущее использование памяти в MB"""
        return self.process.memory_info().rss / 1024 / 1024
        
    def get_cpu_usage(self) -> float:
        """Получить текущую загрузку CPU"""
        return self.process.cpu_percent()
        
    def test_data_collection_performance(self):
        """Тест производительности сбора данных"""
        initial_memory = self.get_memory_usage()
        initial_cpu = self.get_cpu_usage()
        
        # Создаем сборщик данных
        collector = DataCollector()
        collector.set_frequency(1000)  # Высокая частота
        collector.set_buffer_size(10000)
        
        start_time = time.time()
        
        # Собираем данные в течение 5 секунд
        collector.start()
        time.sleep(5.0)
        collector.stop()
        
        end_time = time.time()
        collection_time = end_time - start_time
        
        final_memory = self.get_memory_usage()
        final_cpu = self.get_cpu_usage()
        
        # Проверяем производительность
        data_count = len(collector.data_buffer)
        
        # Проверяем, что данные собирались с высокой производительностью
        self.assertGreater(data_count, 4000)  # Должно быть около 5000 точек
        self.assertLess(collection_time, 5.5)  # Должно быть близко к 5 секундам
        
        # Проверяем использование ресурсов
        memory_increase = final_memory - initial_memory
        self.assertLess(memory_increase, 100)  # Меньше 100 MB
        
        # CPU usage может быть высоким во время сбора
        self.assertGreater(final_cpu, 0)
        
    def test_data_processing_performance(self):
        """Тест производительности обработки данных"""
        # Создаем большие объемы данных
        data_size = 50000
        test_data = np.random.random(data_size)
        
        metrics = ScientificMetrics()
        
        start_time = time.time()
        
        # Обрабатываем данные
        entropy = metrics.calculate_sample_entropy(test_data)
        mad = metrics.calculate_maximum_absolute_deviation(test_data)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Проверяем производительность
        self.assertLess(processing_time, 5.0)  # Должно обрабатываться быстро
        self.assertIsInstance(entropy, float)
        self.assertIsInstance(mad, float)
        
    def test_ml_model_performance(self):
        """Тест производительности ML моделей"""
        # Создаем тестовые данные
        X = np.random.random((1000, 10))
        y = np.random.randint(0, 2, 1000)
        
        ml_models = MLModels()
        
        start_time = time.time()
        
        # Обучаем модель
        model = ml_models.train_random_forest(X, y)
        
        # Делаем предсказания
        predictions = ml_models.predict_with_model(model, X[:100])
        
        end_time = time.time()
        training_time = end_time - start_time
        
        # Проверяем производительность
        self.assertLess(training_time, 30.0)  # Должно обучаться быстро
        self.assertEqual(len(predictions), 100)
        
    def test_memory_leaks(self):
        """Тест на утечки памяти"""
        initial_memory = self.get_memory_usage()
        
        # Создаем и удаляем много объектов
        for i in range(100):
            collector = DataCollector()
            collector.set_buffer_size(1000)
            
            # Собираем немного данных
            collector.start()
            time.sleep(0.01)
            collector.stop()
            
            # Удаляем объект
            del collector
            
            # Принудительная сборка мусора каждые 10 итераций
            if i % 10 == 0:
                gc.collect()
                
        # Принудительная сборка мусора в конце
        gc.collect()
        
        final_memory = self.get_memory_usage()
        memory_increase = final_memory - initial_memory
        
        # Проверяем, что память не утекает сильно
        self.assertLess(memory_increase, 50)  # Меньше 50 MB
        
    def test_concurrent_performance(self):
        """Тест производительности в многопоточной среде"""
        results = []
        errors = []
        
        def worker(worker_id):
            try:
                # Каждый поток создает свой сборщик данных
                collector = DataCollector()
                collector.set_frequency(100)
                collector.set_buffer_size(1000)
                
                # Собираем данные
                collector.start()
                time.sleep(1.0)
                collector.stop()
                
                data_count = len(collector.data_buffer)
                results.append(data_count)
                
            except Exception as e:
                errors.append(str(e))
                
        # Запускаем 5 потоков
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()
            
        # Ждем завершения всех потоков
        for thread in threads:
            thread.join()
            
        # Проверяем результаты
        self.assertEqual(len(errors), 0, f"Ошибки в потоках: {errors}")
        self.assertEqual(len(results), 5)
        
        # Проверяем, что каждый поток собрал данные
        for count in results:
            self.assertGreater(count, 50)  # Каждый поток должен собрать данные
            
    def test_large_dataset_performance(self):
        """Тест производительности с большими наборами данных"""
        # Создаем очень большой набор данных
        data_size = 1000000
        test_data = np.random.random(data_size)
        
        metrics = ScientificMetrics()
        
        start_time = time.time()
        
        # Обрабатываем данные частями
        chunk_size = 10000
        results = []
        
        for i in range(0, data_size, chunk_size):
            chunk = test_data[i:i+chunk_size]
            entropy = metrics.calculate_sample_entropy(chunk)
            results.append(entropy)
            
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Проверяем производительность
        self.assertLess(processing_time, 60.0)  # Должно обрабатываться за разумное время
        self.assertEqual(len(results), data_size // chunk_size)
        
    def test_real_time_processing_performance(self):
        """Тест производительности обработки в реальном времени"""
        processed_count = 0
        
        def callback(data):
            nonlocal processed_count
            processed_count += 1
            
        collector = DataCollector()
        collector.set_frequency(500)
        collector.set_real_time_callback(callback)
        
        start_time = time.time()
        
        # Собираем данные в реальном времени
        collector.start()
        time.sleep(2.0)
        collector.stop()
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Проверяем производительность
        self.assertLess(processing_time, 2.5)  # Должно быть близко к 2 секундам
        self.assertGreater(processed_count, 800)  # Должно быть много обработанных данных
        
    def test_algorithm_scalability(self):
        """Тест масштабируемости алгоритмов"""
        data_sizes = [1000, 5000, 10000, 50000]
        times = []
        
        metrics = ScientificMetrics()
        
        for size in data_sizes:
            test_data = np.random.random(size)
            
            start_time = time.time()
            entropy = metrics.calculate_sample_entropy(test_data)
            end_time = time.time()
            
            processing_time = end_time - start_time
            times.append(processing_time)
            
        # Проверяем, что время растет не экспоненциально
        # (качественный тест на масштабируемость)
        for i in range(1, len(times)):
            # Время не должно расти более чем в 10 раз при увеличении данных в 5 раз
            time_ratio = times[i] / times[i-1]
            size_ratio = data_sizes[i] / data_sizes[i-1]
            
            self.assertLess(time_ratio, size_ratio * 5)
            
    def test_system_stability(self):
        """Тест стабильности системы под нагрузкой"""
        collector = DataCollector()
        collector.set_frequency(1000)
        collector.set_buffer_size(50000)
        
        # Запускаем длительную сессию
        collector.start()
        
        try:
            # Работаем 10 секунд под высокой нагрузкой
            for i in range(10):
                time.sleep(1.0)
                
                # Проверяем стабильность
                current_memory = self.get_memory_usage()
                self.assertLess(current_memory, 500)  # Не должно быть сильного потребления памяти
                
        finally:
            collector.stop()
            
    def test_resource_cleanup(self):
        """Тест очистки ресурсов"""
        initial_memory = self.get_memory_usage()
        
        # Создаем много объектов
        collectors = []
        for i in range(50):
            collector = DataCollector()
            collector.set_buffer_size(1000)
            collectors.append(collector)
            
        # Собираем данные
        for collector in collectors:
            collector.start()
            time.sleep(0.01)
            collector.stop()
            
        # Удаляем все объекты
        del collectors
        gc.collect()
        
        final_memory = self.get_memory_usage()
        memory_increase = final_memory - initial_memory
        
        # Проверяем, что ресурсы освобождены
        self.assertLess(memory_increase, 30)  # Маленькое увеличение памяти
        
    def test_performance_regression(self):
        """Тест регрессии производительности"""
        # Базовые показатели производительности
        baseline_times = {
            'data_collection_5s': 5.0,
            'data_processing_50k': 2.0,
            'ml_training_1k': 10.0
        }
        
        # Тестируем текущую производительность
        current_times = {}
        
        # Тест сбора данных
        collector = DataCollector()
        start_time = time.time()
        collector.start()
        time.sleep(5.0)
        collector.stop()
        current_times['data_collection_5s'] = time.time() - start_time
        
        # Тест обработки данных
        test_data = np.random.random(50000)
        metrics = ScientificMetrics()
        start_time = time.time()
        metrics.calculate_sample_entropy(test_data)
        current_times['data_processing_50k'] = time.time() - start_time
        
        # Тест ML обучения
        X = np.random.random((1000, 5))
        y = np.random.randint(0, 2, 1000)
        ml_models = MLModels()
        start_time = time.time()
        ml_models.train_random_forest(X, y)
        current_times['ml_training_1k'] = time.time() - start_time
        
        # Проверяем, что производительность не ухудшилась более чем на 50%
        for test_name in baseline_times:
            performance_ratio = current_times[test_name] / baseline_times[test_name]
            self.assertLess(performance_ratio, 1.5, 
                          f"Производительность ухудшилась для {test_name}: {performance_ratio:.2f}x")
                          
    def test_multicore_utilization(self):
        """Тест использования нескольких ядер CPU"""
        # Проверяем количество ядер
        cpu_count = psutil.cpu_count()
        self.assertGreater(cpu_count, 0)
        
        # Запускаем нагрузку и проверяем использование ядер
        def cpu_intensive_task():
            # Интенсивные вычисления
            data = np.random.random((10000, 100))
            for _ in range(10):
                result = np.linalg.svd(data)
                
        start_time = time.time()
        
        # Запускаем задачи в нескольких потоках
        threads = []
        for _ in range(min(4, cpu_count)):
            thread = threading.Thread(target=cpu_intensive_task)
            threads.append(thread)
            thread.start()
            
        # Ждем завершения
        for thread in threads:
            thread.join()
            
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Проверяем, что задачи выполнились за разумное время
        self.assertLess(execution_time, 30.0)
        
    def test_disk_io_performance(self):
        """Тест производительности дискового ввода-вывода"""
        test_data = np.random.random(100000)
        
        # Тестируем запись
        start_time = time.time()
        
        filename = 'test_performance_data.npy'
        np.save(filename, test_data)
        
        write_time = time.time() - start_time
        
        # Тестируем чтение
        start_time = time.time()
        
        loaded_data = np.load(filename)
        
        read_time = time.time() - start_time
        
        # Проверяем производительность
        self.assertLess(write_time, 5.0)  # Запись должна быть быстрой
        self.assertLess(read_time, 5.0)   # Чтение должно быть быстрым
        self.assertEqual(len(loaded_data), len(test_data))  # Данные должны совпадать
        
        # Очищаем
        if os.path.exists(filename):
            os.remove(filename)

class TestBenchmark(unittest.TestCase):
    """Тесты бенчмаркинга"""
    
    def setUp(self):
        """Настройка бенчмарка"""
        self.logger = MouseAILogger()
        
    def run_benchmark(self, func, *args, **kwargs) -> Dict[str, float]:
        """Запустить бенчмарк для функции"""
        times = []
        memory_usage = []
        
        # Запускаем функцию несколько раз
        for _ in range(5):
            # Измеряем память до
            process = psutil.Process()
            memory_before = process.memory_info().rss / 1024 / 1024
            
            # Измеряем время выполнения
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            
            # Измеряем память после
            memory_after = process.memory_info().rss / 1024 / 1024
            
            times.append(end_time - start_time)
            memory_usage.append(memory_after - memory_before)
            
        # Возвращаем статистику
        return {
            'mean_time': np.mean(times),
            'std_time': np.std(times),
            'min_time': np.min(times),
            'max_time': np.max(times),
            'mean_memory': np.mean(memory_usage),
            'std_memory': np.std(memory_usage)
        }
        
    def test_data_collection_benchmark(self):
        """Бенчмарк сбора данных"""
        def collect_data():
            collector = DataCollector()
            collector.set_frequency(500)
            collector.set_buffer_size(5000)
            collector.start()
            time.sleep(1.0)
            collector.stop()
            return len(collector.data_buffer)
            
        benchmark_results = self.run_benchmark(collect_data)
        
        # Проверяем результаты бенчмарка
        self.assertLess(benchmark_results['mean_time'], 1.5)
        self.assertGreater(benchmark_results['mean_time'], 0.8)
        self.assertLess(benchmark_results['std_time'], 0.5)
        
    def test_analysis_benchmark(self):
        """Бенчмарк анализа данных"""
        test_data = np.random.random(10000)
        
        def analyze_data():
            metrics = ScientificMetrics()
            entropy = metrics.calculate_sample_entropy(test_data)
            mad = metrics.calculate_maximum_absolute_deviation(test_data)
            return entropy, mad
            
        benchmark_results = self.run_benchmark(analyze_data)
        
        # Проверяем результаты бенчмарка
        self.assertLess(benchmark_results['mean_time'], 5.0)
        self.assertLess(benchmark_results['std_time'], 1.0)
        
    def test_ml_benchmark(self):
        """Бенчмарк ML моделей"""
        X = np.random.random((500, 10))
        y = np.random.randint(0, 2, 500)
        
        def train_model():
            ml_models = MLModels()
            model = ml_models.train_random_forest(X, y)
            predictions = ml_models.predict_with_model(model, X[:50])
            return len(predictions)
            
        benchmark_results = self.run_benchmark(train_model)
        
        # Проверяем результаты бенчмарка
        self.assertLess(benchmark_results['mean_time'], 30.0)
        self.assertLess(benchmark_results['std_time'], 5.0)

if __name__ == '__main__':
    unittest.main()