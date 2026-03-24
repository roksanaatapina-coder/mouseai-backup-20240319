#!/usr/bin/env python3
"""
Test Analysis - Тесты для анализа данных
"""

import unittest
import sys
import os
import time
import numpy as np
from unittest.mock import Mock, patch, MagicMock

# Добавляем путь к проекту
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from mouseai.analysis.scientific_metrics import ScientificMetrics
from mouseai.analysis.ml_models import MLModels
from mouseai.utils import MouseAILogger

class TestScientificMetrics(unittest.TestCase):
    """Тесты для ScientificMetrics"""
    
    def setUp(self):
        """Настройка теста"""
        self.logger = MouseAILogger()
        self.metrics = ScientificMetrics()
        
    def test_initialization(self):
        """Тест инициализации"""
        self.assertIsNotNone(self.metrics)
        self.assertEqual(self.metrics.window_size, 100)
        self.assertEqual(self.metrics.overlap, 50)
        
    def test_calculate_sample_entropy(self):
        """Тест расчета Sample Entropy"""
        # Создаем тестовые данные
        data = np.random.random(1000)
        
        # Рассчитываем Sample Entropy
        entropy = self.metrics.calculate_sample_entropy(data)
        
        # Проверяем результат
        self.assertIsInstance(entropy, float)
        self.assertGreaterEqual(entropy, 0)
        self.assertLessEqual(entropy, 2)  # Теоретический максимум
        
    def test_calculate_maximum_absolute_deviation(self):
        """Тест расчета Maximum Absolute Deviation"""
        # Создаем тестовые данные
        data = np.array([1, 2, 3, 4, 5, 10, 6, 7, 8, 9])
        
        # Рассчитываем MAD
        mad = self.metrics.calculate_maximum_absolute_deviation(data)
        
        # Проверяем результат
        self.assertIsInstance(mad, float)
        self.assertGreater(mad, 0)
        
    def test_calculate_time_to_peak_velocity(self):
        """Тест расчета Time to Peak Velocity"""
        # Создаем тестовые данные (позиция во времени)
        time_data = np.linspace(0, 1, 100)
        position_data = np.sin(time_data * np.pi * 2)  # Синусоидальное движение
        
        # Рассчитываем TTPV
        ttpv = self.metrics.calculate_time_to_peak_velocity(time_data, position_data)
        
        # Проверяем результат
        self.assertIsInstance(ttpv, float)
        self.assertGreaterEqual(ttpv, 0)
        self.assertLessEqual(ttpv, 1)
        
    def test_calculate_movement_efficiency(self):
        """Тест расчета Movement Efficiency"""
        # Создаем тестовые данные
        actual_path = np.array([[0, 0], [1, 1], [2, 2], [3, 3]])
        optimal_path = np.array([[0, 0], [3, 3]])
        
        # Рассчитываем эффективность
        efficiency = self.metrics.calculate_movement_efficiency(actual_path, optimal_path)
        
        # Проверяем результат
        self.assertIsInstance(efficiency, float)
        self.assertGreaterEqual(efficiency, 0)
        self.assertLessEqual(efficiency, 1)
        
    def test_calculate_jerk_metrics(self):
        """Тест расчета Jerk Metrics"""
        # Создаем тестовые данные (позиция во времени)
        time_data = np.linspace(0, 1, 100)
        position_data = np.sin(time_data * np.pi * 2)
        
        # Рассчитываем jerk metrics
        jerk_metrics = self.metrics.calculate_jerk_metrics(time_data, position_data)
        
        # Проверяем результат
        self.assertIsInstance(jerk_metrics, dict)
        self.assertIn('mean_jerk', jerk_metrics)
        self.assertIn('max_jerk', jerk_metrics)
        self.assertIn('jerk_integral', jerk_metrics)
        
    def test_calculate_frequency_analysis(self):
        """Тест частотного анализа"""
        # Создаем тестовые данные
        time_data = np.linspace(0, 1, 1000)
        signal_data = np.sin(time_data * 2 * np.pi * 5) + 0.1 * np.random.random(1000)  # 5 Гц сигнал
        
        # Рассчитываем частотный анализ
        freq_analysis = self.metrics.calculate_frequency_analysis(time_data, signal_data)
        
        # Проверяем результат
        self.assertIsInstance(freq_analysis, dict)
        self.assertIn('dominant_frequency', freq_analysis)
        self.assertIn('frequency_spectrum', freq_analysis)
        
        # Проверяем, что доминирующая частота близка к 5 Гц
        self.assertAlmostEqual(freq_analysis['dominant_frequency'], 5, delta=0.5)
        
    def test_calculate_biomechanical_metrics(self):
        """Тест биомеханических метрик"""
        # Создаем тестовые данные
        time_data = np.linspace(0, 1, 100)
        position_data = np.sin(time_data * np.pi * 2)
        
        # Рассчитываем биомеханические метрики
        bio_metrics = self.metrics.calculate_biomechanical_metrics(time_data, position_data)
        
        # Проверяем результат
        self.assertIsInstance(bio_metrics, dict)
        self.assertIn('velocity', bio_metrics)
        self.assertIn('acceleration', bio_metrics)
        self.assertIn('jerk', bio_metrics)
        
    def test_calculate_pattern_recognition(self):
        """Тест распознавания паттернов"""
        # Создаем тестовые данные с повторяющимся паттерном
        pattern = np.sin(np.linspace(0, 2*np.pi, 50))
        data = np.tile(pattern, 10)  # Повторяем паттерн 10 раз
        
        # Рассчитываем распознавание паттернов
        patterns = self.metrics.calculate_pattern_recognition(data)
        
        # Проверяем результат
        self.assertIsInstance(patterns, dict)
        self.assertIn('repeating_patterns', patterns)
        self.assertIn('pattern_length', patterns)
        self.assertIn('pattern_similarity', patterns)
        
        # Проверяем, что паттерн был распознан
        self.assertGreater(len(patterns['repeating_patterns']), 0)
        
    def test_analyze_movement_quality(self):
        """Тест анализа качества движений"""
        # Создаем тестовые данные
        time_data = np.linspace(0, 1, 100)
        position_data = np.sin(time_data * np.pi * 2)
        
        # Анализируем качество движений
        quality = self.metrics.analyze_movement_quality(time_data, position_data)
        
        # Проверяем результат
        self.assertIsInstance(quality, dict)
        self.assertIn('smoothness', quality)
        self.assertIn('accuracy', quality)
        self.assertIn('consistency', quality)
        
    def test_calculate_reaction_time(self):
        """Тест расчета времени реакции"""
        # Создаем тестовые данные
        stimulus_time = 0.5
        response_times = [0.6, 0.65, 0.58, 0.72, 0.61]
        
        # Рассчитываем время реакции
        reaction_time = self.metrics.calculate_reaction_time(stimulus_time, response_times)
        
        # Проверяем результат
        self.assertIsInstance(reaction_time, dict)
        self.assertIn('mean', reaction_time)
        self.assertIn('std', reaction_time)
        self.assertIn('median', reaction_time)
        
        # Проверяем, что среднее время реакции положительное
        self.assertGreater(reaction_time['mean'], 0)
        
    def test_calculate_tracking_accuracy(self):
        """Тест расчета точности отслеживания"""
        # Создаем тестовые данные
        target_positions = np.array([[0, 0], [1, 1], [2, 2], [3, 3]])
        actual_positions = np.array([[0.1, 0.1], [1.1, 1.1], [1.9, 1.9], [3.1, 3.1]])
        
        # Рассчитываем точность отслеживания
        accuracy = self.metrics.calculate_tracking_accuracy(target_positions, actual_positions)
        
        # Проверяем результат
        self.assertIsInstance(accuracy, dict)
        self.assertIn('mean_error', accuracy)
        self.assertIn('max_error', accuracy)
        self.assertIn('rmse', accuracy)
        
        # Проверяем, что ошибки небольшие
        self.assertLess(accuracy['mean_error'], 0.5)
        
    def test_calculate_fitts_law_metrics(self):
        """Тест метрик закона Фиттса"""
        # Создаем тестовые данные
        movement_time = 0.5
        distance = 100
        target_width = 20
        
        # Рассчитываем метрики закона Фиттса
        fitts_metrics = self.metrics.calculate_fitts_law_metrics(movement_time, distance, target_width)
        
        # Проверяем результат
        self.assertIsInstance(fitts_metrics, dict)
        self.assertIn('index_of_difficulty', fitts_metrics)
        self.assertIn('throughput', fitts_metrics)
        
        # Проверяем, что индекс сложности положительный
        self.assertGreater(fitts_metrics['index_of_difficulty'], 0)
        
    def test_calculate_hand_eye_coordination(self):
        """Тест расчета координации глаз и рук"""
        # Создаем тестовые данные
        visual_stimuli = np.array([0.1, 0.3, 0.5, 0.7, 0.9])
        motor_responses = np.array([0.12, 0.31, 0.52, 0.71, 0.89])
        
        # Рассчитываем координацию
        coordination = self.metrics.calculate_hand_eye_coordination(visual_stimuli, motor_responses)
        
        # Проверяем результат
        self.assertIsInstance(coordination, dict)
        self.assertIn('correlation', coordination)
        self.assertIn('latency', coordination)
        self.assertIn('accuracy', coordination)
        
        # Проверяем, что корреляция высокая
        self.assertGreater(coordination['correlation'], 0.8)
        
    def test_calculate_fatigue_metrics(self):
        """Тест метрик усталости"""
        # Создаем тестовые данные (снижающаяся производительность)
        performance_data = np.linspace(1.0, 0.5, 100)  # Постепенное снижение
        
        # Рассчитываем метрики усталости
        fatigue = self.metrics.calculate_fatigue_metrics(performance_data)
        
        # Проверяем результат
        self.assertIsInstance(fatigue, dict)
        self.assertIn('trend', fatigue)
        self.assertIn('rate_of_decline', fatigue)
        self.assertIn('fatigue_index', fatigue)
        
        # Проверяем, что обнаружена усталость
        self.assertLess(fatigue['trend'], 0)
        
    def test_calculate_stress_indicators(self):
        """Тест индикаторов стресса"""
        # Создаем тестовые данные
        heart_rate = np.array([70, 75, 80, 85, 90])
        movement_variability = np.array([0.1, 0.2, 0.3, 0.4, 0.5])
        
        # Рассчитываем индикаторы стресса
        stress = self.metrics.calculate_stress_indicators(heart_rate, movement_variability)
        
        # Проверяем результат
        self.assertIsInstance(stress, dict)
        self.assertIn('physiological_stress', stress)
        self.assertIn('behavioral_stress', stress)
        self.assertIn('overall_stress', stress)
        
    def test_calculate_learning_curve(self):
        """Тест кривой обучения"""
        # Создаем тестовые данные (улучшающаяся производительность)
        session_data = [
            {'session': 1, 'performance': 0.3},
            {'session': 2, 'performance': 0.4},
            {'session': 3, 'performance': 0.5},
            {'session': 4, 'performance': 0.6},
            {'session': 5, 'performance': 0.7}
        ]
        
        # Рассчитываем кривую обучения
        learning_curve = self.metrics.calculate_learning_curve(session_data)
        
        # Проверяем результат
        self.assertIsInstance(learning_curve, dict)
        self.assertIn('improvement_rate', learning_curve)
        self.assertIn('plateau_detection', learning_curve)
        self.assertIn('skill_acquisition', learning_curve)
        
        # Проверяем, что обнаружено улучшение
        self.assertGreater(learning_curve['improvement_rate'], 0)
        
    def test_calculate_performance_metrics(self):
        """Тест метрик производительности"""
        # Создаем тестовые данные
        accuracy_data = np.array([0.8, 0.85, 0.9, 0.92, 0.88])
        speed_data = np.array([0.5, 0.45, 0.4, 0.38, 0.42])
        consistency_data = np.array([0.95, 0.93, 0.94, 0.96, 0.92])
        
        # Рассчитываем метрики производительности
        performance = self.metrics.calculate_performance_metrics(accuracy_data, speed_data, consistency_data)
        
        # Проверяем результат
        self.assertIsInstance(performance, dict)
        self.assertIn('accuracy_score', performance)
        self.assertIn('speed_score', performance)
        self.assertIn('consistency_score', performance)
        self.assertIn('overall_performance', performance)
        
    def test_calculate_error_analysis(self):
        """Тест анализа ошибок"""
        # Создаем тестовые данные
        target_data = np.array([1, 2, 3, 4, 5])
        actual_data = np.array([1.1, 2.2, 2.8, 4.1, 4.9])
        
        # Рассчитываем анализ ошибок
        error_analysis = self.metrics.calculate_error_analysis(target_data, actual_data)
        
        # Проверяем результат
        self.assertIsInstance(error_analysis, dict)
        self.assertIn('mean_error', error_analysis)
        self.assertIn('error_distribution', error_analysis)
        self.assertIn('error_patterns', error_analysis)
        
    def test_calculate_timing_metrics(self):
        """Тест метрик времени"""
        # Создаем тестовые данные
        timestamps = np.linspace(0, 1, 100)
        events = np.array([0.1, 0.3, 0.5, 0.7, 0.9])
        
        # Рассчитываем метрики времени
        timing = self.metrics.calculate_timing_metrics(timestamps, events)
        
        # Проверяем результат
        self.assertIsInstance(timing, dict)
        self.assertIn('mean_interval', timing)
        self.assertIn('interval_variance', timing)
        self.assertIn('timing_precision', timing)
        
    def test_calculate_complexity_metrics(self):
        """Тест метрик сложности"""
        # Создаем тестовые данные
        movement_data = np.random.random((100, 2))
        
        # Рассчитываем метрики сложности
        complexity = self.metrics.calculate_complexity_metrics(movement_data)
        
        # Проверяем результат
        self.assertIsInstance(complexity, dict)
        self.assertIn('fractal_dimension', complexity)
        self.assertIn('lyapunov_exponent', complexity)
        self.assertIn('approximate_entropy', complexity)

class TestMLModels(unittest.TestCase):
    """Тесты для MLModels"""
    
    def setUp(self):
        """Настройка теста"""
        self.logger = MouseAILogger()
        self.ml_models = MLModels()
        
    def test_initialization(self):
        """Тест инициализации"""
        self.assertIsNotNone(self.ml_models)
        self.assertIsNotNone(self.ml_models.models)
        self.assertEqual(len(self.ml_models.models), 3)  # 3 модели по умолчанию
        
    def test_train_random_forest(self):
        """Тест обучения Random Forest"""
        # Создаем тестовые данные
        X = np.random.random((100, 5))
        y = np.random.randint(0, 2, 100)
        
        # Обучаем модель
        model = self.ml_models.train_random_forest(X, y)
        
        # Проверяем результат
        self.assertIsNotNone(model)
        self.assertTrue(hasattr(model, 'predict'))
        
    def test_train_svm(self):
        """Тест обучения SVM"""
        # Создаем тестовые данные
        X = np.random.random((100, 5))
        y = np.random.randint(0, 2, 100)
        
        # Обучаем модель
        model = self.ml_models.train_svm(X, y)
        
        # Проверяем результат
        self.assertIsNotNone(model)
        self.assertTrue(hasattr(model, 'predict'))
        
    def test_train_neural_network(self):
        """Тест обучения нейронной сети"""
        # Создаем тестовые данные
        X = np.random.random((100, 5))
        y = np.random.randint(0, 2, 100)
        
        # Обучаем модель
        model = self.ml_models.train_neural_network(X, y)
        
        # Проверяем результат
        self.assertIsNotNone(model)
        self.assertTrue(hasattr(model, 'predict'))
        
    def test_predict_with_model(self):
        """Тест предсказания с моделью"""
        # Создаем тестовые данные
        X_train = np.random.random((100, 5))
        y_train = np.random.randint(0, 2, 100)
        X_test = np.random.random((10, 5))
        
        # Обучаем модель
        model = self.ml_models.train_random_forest(X_train, y_train)
        
        # Делаем предсказание
        predictions = self.ml_models.predict_with_model(model, X_test)
        
        # Проверяем результат
        self.assertIsInstance(predictions, np.ndarray)
        self.assertEqual(len(predictions), 10)
        
    def test_evaluate_model(self):
        """Тест оценки модели"""
        # Создаем тестовые данные
        X_train = np.random.random((100, 5))
        y_train = np.random.randint(0, 2, 100)
        X_test = np.random.random((20, 5))
        y_test = np.random.randint(0, 2, 20)
        
        # Обучаем модель
        model = self.ml_models.train_random_forest(X_train, y_train)
        
        # Оцениваем модель
        metrics = self.ml_models.evaluate_model(model, X_test, y_test)
        
        # Проверяем результат
        self.assertIsInstance(metrics, dict)
        self.assertIn('accuracy', metrics)
        self.assertIn('precision', metrics)
        self.assertIn('recall', metrics)
        self.assertIn('f1_score', metrics)
        
    def test_cross_validation(self):
        """Тест кросс-валидации"""
        # Создаем тестовые данные
        X = np.random.random((100, 5))
        y = np.random.randint(0, 2, 100)
        
        # Проводим кросс-валидацию
        cv_scores = self.ml_models.cross_validation(X, y, cv=3)
        
        # Проверяем результат
        self.assertIsInstance(cv_scores, np.ndarray)
        self.assertEqual(len(cv_scores), 3)
        
    def test_feature_importance(self):
        """Тест важности признаков"""
        # Создаем тестовые данные
        X = np.random.random((100, 5))
        y = np.random.randint(0, 2, 100)
        
        # Обучаем модель
        model = self.ml_models.train_random_forest(X, y)
        
        # Получаем важность признаков
        importance = self.ml_models.get_feature_importance(model)
        
        # Проверяем результат
        self.assertIsInstance(importance, np.ndarray)
        self.assertEqual(len(importance), 5)
        
    def test_hyperparameter_tuning(self):
        """Тест подбора гиперпараметров"""
        # Создаем тестовые данные
        X = np.random.random((50, 5))
        y = np.random.randint(0, 2, 50)
        
        # Подбираем гиперпараметры
        best_params = self.ml_models.hyperparameter_tuning(X, y, model_type='random_forest', cv=2)
        
        # Проверяем результат
        self.assertIsInstance(best_params, dict)
        
    def test_ensemble_prediction(self):
        """Тест ансамблевого предсказания"""
        # Создаем тестовые данные
        X_train = np.random.random((100, 5))
        y_train = np.random.randint(0, 2, 100)
        X_test = np.random.random((10, 5))
        
        # Обучаем ансамбль
        ensemble = self.ml_models.train_ensemble(X_train, y_train)
        
        # Делаем предсказание
        predictions = self.ml_models.ensemble_predict(ensemble, X_test)
        
        # Проверяем результат
        self.assertIsInstance(predictions, np.ndarray)
        self.assertEqual(len(predictions), 10)
        
    def test_model_comparison(self):
        """Тест сравнения моделей"""
        # Создаем тестовые данные
        X_train = np.random.random((100, 5))
        y_train = np.random.randint(0, 2, 100)
        X_test = np.random.random((20, 5))
        y_test = np.random.randint(0, 2, 20)
        
        # Сравниваем модели
        comparison = self.ml_models.compare_models(X_train, y_train, X_test, y_test)
        
        # Проверяем результат
        self.assertIsInstance(comparison, dict)
        self.assertIn('random_forest', comparison)
        self.assertIn('svm', comparison)
        self.assertIn('neural_network', comparison)
        
    def test_save_and_load_model(self):
        """Тест сохранения и загрузки модели"""
        # Создаем тестовые данные
        X = np.random.random((100, 5))
        y = np.random.randint(0, 2, 100)
        
        # Обучаем модель
        model = self.ml_models.train_random_forest(X, y)
        
        # Сохраняем модель
        filename = 'test_model.pkl'
        self.ml_models.save_model(model, filename)
        
        # Проверяем, что файл создан
        self.assertTrue(os.path.exists(filename))
        
        # Загружаем модель
        loaded_model = self.ml_models.load_model(filename)
        
        # Проверяем, что модель загружена
        self.assertIsNotNone(loaded_model)
        
        # Очищаем
        if os.path.exists(filename):
            os.remove(filename)

if __name__ == '__main__':
    unittest.main()