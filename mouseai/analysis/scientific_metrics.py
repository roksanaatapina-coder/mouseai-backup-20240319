#!/usr/bin/env python3
"""
ScientificMetrics - Научные метрики из mousetrap и исследований
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import math

@dataclass
class ScientificMetrics:
    """Результаты научного анализа"""
    sample_entropy: float
    maximum_absolute_deviation: float
    area_under_curve: float
    bimodality_coefficient: float
    time_to_peak_velocity: float
    movement_efficiency: float
    trajectory_complexity: float
    jerk_metric: float

class ScientificMetricsCalculator:
    """Калькулятор научных метрик с оптимизацией производительности"""
    
    def __init__(self, sampling_rate: int = 100, window_size: int = 10):
        self.sampling_rate = sampling_rate  # Hz
        self.window_size = window_size      # Для скользящего окна
        self._cache = {}                    # Кэш для промежуточных вычислений
        self._stats = {
            'total_calculations': 0,
            'cache_hits': 0,
            'processing_time': 0.0
        }
        
    def calculate_all_metrics(self, mouse_data: List[Dict]) -> ScientificMetrics:
        """Рассчитать все научные метрики с оптимизацией"""
        import time
        start_time = time.time()
        
        if not mouse_data or len(mouse_data) < 10:
            return self._get_empty_metrics()
            
        # Проверяем кэш
        data_hash = hash(str(mouse_data[:100]))  # Хэшируем первые 100 элементов
        if data_hash in self._cache:
            self._stats['cache_hits'] += 1
            return self._cache[data_hash]
            
        # Преобразуем данные
        positions = self._extract_positions(mouse_data)
        velocities = self._calculate_velocities(positions)
        accelerations = self._calculate_accelerations(velocities)
        
        # Рассчитываем метрики с оптимизацией
        sample_entropy = self._calculate_sample_entropy(positions)
        mad = self._calculate_maximum_absolute_deviation(positions)
        auc = self._calculate_area_under_curve(velocities)
        bimodality = self._calculate_bimodality_coefficient(velocities)
        ttpv = self._calculate_time_to_peak_velocity(velocities)
        efficiency = self._calculate_movement_efficiency(positions)
        complexity = self._calculate_trajectory_complexity(positions)
        jerk = self._calculate_jerk_metric(accelerations)
        
        result = ScientificMetrics(
            sample_entropy=sample_entropy,
            maximum_absolute_deviation=mad,
            area_under_curve=auc,
            bimodality_coefficient=bimodality,
            time_to_peak_velocity=ttpv,
            movement_efficiency=efficiency,
            trajectory_complexity=complexity,
            jerk_metric=jerk
        )
        
        # Кэшируем результат
        self._cache[data_hash] = result
        self._stats['total_calculations'] += 1
        self._stats['processing_time'] += time.time() - start_time
        
        # Ограничиваем размер кэша
        if len(self._cache) > 100:
            # Удаляем старые записи (простая стратегия)
            keys_to_remove = list(self._cache.keys())[:50]
            for key in keys_to_remove:
                del self._cache[key]
                
        return result
        
    def _extract_positions(self, mouse_data: List[Dict]) -> np.ndarray:
        """Извлечь позиции из данных мыши"""
        positions = []
        for data in mouse_data:
            if 'x' in data and 'y' in data:
                positions.append([data['x'], data['y']])
        return np.array(positions)
        
    def _calculate_velocities(self, positions: np.ndarray) -> np.ndarray:
        """Рассчитать скорости"""
        if len(positions) < 2:
            return np.array([])
            
        velocities = np.diff(positions, axis=0) * self.sampling_rate
        return np.linalg.norm(velocities, axis=1)
        
    def _calculate_accelerations(self, velocities: np.ndarray) -> np.ndarray:
        """Рассчитать ускорения"""
        if len(velocities) < 2:
            return np.array([])
            
        return np.diff(velocities) * self.sampling_rate
        
    def _calculate_sample_entropy(self, positions: np.ndarray) -> float:
        """
        Sample Entropy (SampEn) - мера сложности и регулярности траектории
        Чем выше значение, тем более сложная и нерегулярная траектория
        """
        try:
            if len(positions) < 10:
                return 0.0
                
            # Параметры для SampEn (стандартные для движений)
            m = 2  # длина шаблона
            r = 0.2 * np.std(positions)  # порог схожести
            
            if r == 0:
                return 0.0
                
            def _template_match(data, m, r):
                """Вспомогательная функция для SampEn с оптимизацией"""
                N = len(data)
                if N <= m:
                    return 0
                    
                # Создаем шаблоны
                templates = np.array([data[i:i+m] for i in range(N-m)])
                
                # Оптимизированное сравнение шаблонов
                matches = 0
                n_templates = len(templates)
                
                # Используем векторизованные операции для ускорения
                for i in range(n_templates):
                    # Векторизованное сравнение с другими шаблонами
                    diff = np.abs(templates[i+1:] - templates[i])
                    max_diff = np.max(diff, axis=1)
                    matches += np.sum(max_diff <= r)
                            
                return matches / (n_templates * (n_templates - 1) / 2) if n_templates > 1 else 0
                
            # Рассчитываем для X и Y координат отдельно
            sampen_x = _template_match(positions[:, 0], m, r)
            sampen_y = _template_match(positions[:, 1], m, r)
            
            # Возвращаем среднее
            return (sampen_x + sampen_y) / 2
            
        except Exception:
            return 0.0
            
    def _calculate_maximum_absolute_deviation(self, positions: np.ndarray) -> float:
        """
        Maximum Absolute Deviation (MAD) - максимальное отклонение от прямой линии
        Показывает, насколько траектория отклоняется от идеальной прямой
        """
        try:
            if len(positions) < 2:
                return 0.0
                
            # Начальная и конечная точки
            start = positions[0]
            end = positions[-1]
            
            # Если начальная и конечная точки совпадают
            if np.allclose(start, end):
                return 0.0
                
            # Векторизованное вычисление расстояний
            # Создаем вектор направления прямой
            line_vector = end - start
            line_length = np.linalg.norm(line_vector)
            
            if line_length == 0:
                return 0.0
                
            # Нормализуем вектор направления
            line_unit = line_vector / line_length
            
            # Вычисляем проекции всех точек на прямую
            point_vectors = positions - start
            projections = np.dot(point_vectors, line_unit)
            
            # Ограничиваем проекции диапазоном отрезка
            projections = np.clip(projections, 0, line_length)
            
            # Вычисляем точки на прямой
            projected_points = start + projections[:, np.newaxis] * line_unit
            
            # Вычисляем расстояния от точек до прямой
            distances = np.linalg.norm(positions - projected_points, axis=1)
            
            return np.max(distances) if len(distances) > 0 else 0.0
            
        except Exception:
            return 0.0
            
    def _calculate_area_under_curve(self, velocities: np.ndarray) -> float:
        """
        Area Under Curve (AUC) - площадь под кривой скорости
        Показывает общую "энергию" движения
        """
        try:
            if len(velocities) < 2:
                return 0.0
                
            # Проверяем на NaN и бесконечности
            velocities = np.nan_to_num(velocities, nan=0.0, posinf=0.0, neginf=0.0)
            
            # Интегрируем скорость по времени
            time_step = 1.0 / self.sampling_rate
            
            # Используем более устойчивое интегрирование
            if len(velocities) == 2:
                return velocities[0] * time_step
            else:
                return np.trapz(velocities, dx=time_step)
            
        except Exception:
            return 0.0
            
    def _calculate_bimodality_coefficient(self, velocities: np.ndarray) -> float:
        """
        Bimodality Coefficient (BC) - показатель наличия двух режимов скорости
        BC > 0.55 указывает на бимодальное распределение (два режима: медленный и быстрый)
        """
        try:
            if len(velocities) < 10:
                return 0.0
                
            # Рассчитываем статистики
            mean_vel = np.mean(velocities)
            std_vel = np.std(velocities)
            skewness = self._calculate_skewness(velocities)
            kurtosis = self._calculate_kurtosis(velocities)
            
            if std_vel == 0:
                return 0.0
                
            # Формула Bimodality Coefficient
            bc = (skewness**2 + 1) / (kurtosis + 3 * ((len(velocities) - 1)**2) / ((len(velocities) - 2) * (len(velocities) - 3)))
            
            return bc
            
        except Exception:
            return 0.0
            
    def _calculate_time_to_peak_velocity(self, velocities: np.ndarray) -> float:
        """
        Time to Peak Velocity (TTPV) - время достижения максимальной скорости
        Показывает взрывную силу и реакцию
        """
        try:
            if len(velocities) < 2:
                return 0.0
                
            max_vel_idx = np.argmax(velocities)
            time_step = 1.0 / self.sampling_rate
            
            return max_vel_idx * time_step
            
        except Exception:
            return 0.0
            
    def _calculate_movement_efficiency(self, positions: np.ndarray) -> float:
        """
        Movement Efficiency - эффективность движения
        Отношение прямого расстояния к фактическому пройденному пути
        """
        try:
            if len(positions) < 2:
                return 0.0
                
            # Прямое расстояние
            start = positions[0]
            end = positions[-1]
            direct_distance = np.linalg.norm(end - start)
            
            # Фактический путь
            path_distance = 0.0
            for i in range(1, len(positions)):
                path_distance += np.linalg.norm(positions[i] - positions[i-1])
                
            if path_distance == 0:
                return 0.0
                
            return direct_distance / path_distance
            
        except Exception:
            return 0.0
            
    def _calculate_trajectory_complexity(self, positions: np.ndarray) -> float:
        """
        Trajectory Complexity - сложность траектории
        Основана на фрактальной размерности и изменчивости направления
        """
        try:
            if len(positions) < 10:
                return 0.0
                
            # Рассчитываем изменения направления
            directions = []
            for i in range(1, len(positions)):
                vec = positions[i] - positions[i-1]
                if np.linalg.norm(vec) > 0:
                    angle = np.arctan2(vec[1], vec[0])
                    directions.append(angle)
                    
            if len(directions) < 5:
                return 0.0
                
            # Изменчивость направления
            direction_changes = np.diff(directions)
            complexity = np.std(direction_changes)
            
            return complexity
            
        except Exception:
            return 0.0
            
    def _calculate_jerk_metric(self, accelerations: np.ndarray) -> float:
        """
        Jerk Metric - показатель плавности движения
        Рассчитывается как интеграл от jerk (третья производная положения)
        """
        try:
            if len(accelerations) < 3:  # Нужно минимум 3 точки для второй производной
                return 0.0
                
            # Проверяем на NaN и бесконечности
            accelerations = np.nan_to_num(accelerations, nan=0.0, posinf=0.0, neginf=0.0)
            
            # Рассчитываем jerk (производная ускорения)
            jerks = np.diff(accelerations)
            
            # Фильтрация выбросов (удаляем значения за пределами 3 сигм)
            if len(jerks) > 0:
                jerk_mean = np.mean(jerks)
                jerk_std = np.std(jerks)
                if jerk_std > 0:
                    jerks = jerks[np.abs(jerks - jerk_mean) <= 3 * jerk_std]
            
            # Интегрируем jerk
            time_step = 1.0 / self.sampling_rate
            
            if len(jerks) == 0:
                return 0.0
            elif len(jerks) == 1:
                return np.abs(jerks[0]) * time_step
            else:
                jerk_integral = np.trapz(np.abs(jerks), dx=time_step)
                return jerk_integral
            
        except Exception:
            return 0.0
            
    def _calculate_skewness(self, data: np.ndarray) -> float:
        """Рассчитать асимметрию распределения с оптимизацией"""
        try:
            if len(data) < 3:
                return 0.0
                
            # Проверяем на NaN и бесконечности
            data = np.nan_to_num(data, nan=0.0, posinf=0.0, neginf=0.0)
            
            mean_val = np.mean(data)
            std_val = np.std(data)
            
            if std_val == 0:
                return 0.0
                
            n = len(data)
            # Оптимизированное вычисление асимметрии
            centered_data = (data - mean_val) / std_val
            skewness = (n / ((n-1) * (n-2))) * np.sum(centered_data ** 3)
            return skewness
        except:
            return 0.0
            
    def _calculate_kurtosis(self, data: np.ndarray) -> float:
        """Рассчитать эксцесс распределения с оптимизацией"""
        try:
            if len(data) < 4:
                return 0.0
                
            # Проверяем на NaN и бесконечности
            data = np.nan_to_num(data, nan=0.0, posinf=0.0, neginf=0.0)
            
            mean_val = np.mean(data)
            std_val = np.std(data)
            
            if std_val == 0:
                return 0.0
                
            n = len(data)
            # Оптимизированное вычисление эксцесса
            centered_data = (data - mean_val) / std_val
            kurtosis = (n * (n+1) / ((n-1) * (n-2) * (n-3))) * np.sum(centered_data ** 4)
            kurtosis -= (3 * (n-1)**2) / ((n-2) * (n-3))
            return kurtosis
        except:
            return 0.0
            
    def _get_empty_metrics(self) -> ScientificMetrics:
        """Получить пустые метрики"""
        return ScientificMetrics(
            sample_entropy=0.0,
            maximum_absolute_deviation=0.0,
            area_under_curve=0.0,
            bimodality_coefficient=0.0,
            time_to_peak_velocity=0.0,
            movement_efficiency=0.0,
            trajectory_complexity=0.0,
            jerk_metric=0.0
        )

class MetricsInterpreter:
    """Интерпретатор научных метрик"""
    
    @staticmethod
    def interpret_metrics(metrics: ScientificMetrics) -> Dict[str, str]:
        """Интерпретировать метрики в понятные рекомендации с улучшенной логикой"""
        
        interpretations = {}
        
        # Sample Entropy (Сложность движений)
        if metrics.sample_entropy > 0.6:
            interpretations['sample_entropy'] = "Очень высокая сложность - отличная адаптивность и непредсказуемость"
        elif metrics.sample_entropy > 0.4:
            interpretations['sample_entropy'] = "Высокая сложность - хорошая адаптивность"
        elif metrics.sample_entropy > 0.2:
            interpretations['sample_entropy'] = "Средняя сложность движений"
        elif metrics.sample_entropy > 0.1:
            interpretations['sample_entropy'] = "Низкая сложность - возможно, шаблонные движения"
        else:
            interpretations['sample_entropy'] = "Очень низкая сложность - рекомендуется разнообразить движения"
            
        # Maximum Absolute Deviation (Точность)
        if metrics.maximum_absolute_deviation < 10:
            interpretations['mad'] = "Отличная точность движений - минимальные отклонения от прямой"
        elif metrics.maximum_absolute_deviation < 25:
            interpretations['mad'] = "Хорошая точность движений"
        elif metrics.maximum_absolute_deviation < 50:
            interpretations['mad'] = "Умеренные отклонения - нормально для сложных движений"
        elif metrics.maximum_absolute_deviation < 100:
            interpretations['mad'] = "Большие отклонения - работайте над точностью"
        else:
            interpretations['mad'] = "Очень большие отклонения - серьезные проблемы с точностью"
            
        # Bimodality Coefficient (Режимы скорости)
        if metrics.bimodality_coefficient > 0.7:
            interpretations['bimodality'] = "Очень выраженный бимодальный режим - отличный контроль скорости"
        elif metrics.bimodality_coefficient > 0.55:
            interpretations['bimodality'] = "Два режима скорости - хороший контроль"
        elif metrics.bimodality_coefficient > 0.4:
            interpretations['bimodality'] = "Умеренное бимодальное распределение"
        elif metrics.bimodality_coefficient > 0.25:
            interpretations['bimodality'] = "Слабое бимодальное распределение - ограниченная вариативность"
        else:
            interpretations['bimodality'] = "Один режим скорости - недостаточная вариативность"
            
        # Time to Peak Velocity (Реакция)
        if metrics.time_to_peak_velocity < 0.05:
            interpretations['ttpv'] = "Очень быстрое достижение пика - отличная реакция и взрывная сила"
        elif metrics.time_to_peak_velocity < 0.1:
            interpretations['ttpv'] = "Быстрое достижение пика скорости - хорошая реакция"
        elif metrics.time_to_peak_velocity < 0.2:
            interpretations['ttpv'] = "Умеренное время до пика скорости"
        elif metrics.time_to_peak_velocity < 0.4:
            interpretations['ttpv'] = "Медленное достижение пика - тренируйте взрывную силу"
        else:
            interpretations['ttpv'] = "Очень медленное достижение пика - серьезные проблемы с реакцией"
            
        # Movement Efficiency (Эффективность)
        if metrics.movement_efficiency > 0.9:
            interpretations['efficiency'] = "Очень высокая эффективность - почти идеальные траектории"
        elif metrics.movement_efficiency > 0.8:
            interpretations['efficiency'] = "Высокая эффективность движений"
        elif metrics.movement_efficiency > 0.7:
            interpretations['efficiency'] = "Хорошая эффективность"
        elif metrics.movement_efficiency > 0.6:
            interpretations['efficiency'] = "Умеренная эффективность"
        elif metrics.movement_efficiency > 0.4:
            interpretations['efficiency'] = "Низкая эффективность - много лишних движений"
        else:
            interpretations['efficiency'] = "Очень низкая эффективность - серьезные проблемы с траекториями"
            
        # Jerk Metric (Плавность)
        if metrics.jerk_metric < 5:
            interpretations['jerk'] = "Очень плавные движения - отличная координация"
        elif metrics.jerk_metric < 10:
            interpretations['jerk'] = "Плавные движения - хорошая координация"
        elif metrics.jerk_metric < 25:
            interpretations['jerk'] = "Умеренные рывки - нормально"
        elif metrics.jerk_metric < 50:
            interpretations['jerk'] = "Заметные рывки - работайте над плавностью"
        elif metrics.jerk_metric < 100:
            interpretations['jerk'] = "Сильные рывки - серьезные проблемы с плавностью"
        else:
            interpretations['jerk'] = "Очень сильные рывки - движения нестабильны"
            
        return interpretations
        
    @staticmethod
    def get_game_specific_insights(metrics: ScientificMetrics, game_category: str) -> List[str]:
        """Получить рекомендации для конкретной игры с улучшенной логикой"""
        
        insights = []
        
        if game_category in ['tactical_fps', 'hero_fps']:
            # Для FPS критически важны скорость реакции и точность
            if metrics.time_to_peak_velocity > 0.15:
                insights.append("Для FPS: тренируйте быстрое достижение максимальной скорости (цель: <150мс)")
            if metrics.movement_efficiency < 0.8:
                insights.append("Для FPS: работайте над прямыми и эффективными движениями (цель: >80%)")
            if metrics.jerk_metric > 20:
                insights.append("Для FPS: уменьшайте рывки для более точного прицеливания (цель: <20)")
            if metrics.maximum_absolute_deviation > 20:
                insights.append("Для FPS: улучшайте точность движений (цель: <20px отклонения)")
            if metrics.bimodality_coefficient < 0.4:
                insights.append("Для FPS: развивайте переключение между скоростными режимами")
                
        elif game_category == 'battle_royale':
            # Для Battle Royale важна непредсказуемость и вариативность
            if metrics.sample_entropy < 0.3:
                insights.append("Для Battle Royale: развивайте более сложные и непредсказуемые движения")
            if metrics.bimodality_coefficient < 0.4:
                insights.append("Для Battle Royale: тренируйте переключение между скоростными режимами")
            if metrics.trajectory_complexity < 0.5:
                insights.append("Для Battle Royale: усложняйте траектории движений для непредсказуемости")
                
        elif game_category == 'survival':
            # Для Survival важна точность и эффективность
            if metrics.maximum_absolute_deviation > 30:
                insights.append("Для Survival: работайте над точностью прицеливания")
            if metrics.movement_efficiency < 0.6:
                insights.append("Для Survival: оптимизируйте траектории движений")
            if metrics.jerk_metric > 40:
                insights.append("Для Survival: уменьшайте рывки для стабильности прицеливания")
                
        elif game_category == 'rpg':
            # Для RPG важна плавность и контроль
            if metrics.jerk_metric > 30:
                insights.append("Для RPG: работайте над плавностью движений для лучшего контроля")
            if metrics.time_to_peak_velocity > 0.3:
                insights.append("Для RPG: тренируйте более плавное управление скоростью")
                
        elif game_category == 'strategy':
            # Для Strategy важна точность и эффективность
            if metrics.maximum_absolute_deviation > 25:
                insights.append("Для Strategy: улучшайте точность кликов и движений")
            if metrics.movement_efficiency < 0.7:
                insights.append("Для Strategy: оптимизируйте траектории для быстрого управления")
                
        # Универсальные рекомендации
        if metrics.sample_entropy < 0.2:
            insights.append("Универсально: развивайте более разнообразные и непредсказуемые движения")
        if metrics.bimodality_coefficient < 0.3:
            insights.append("Универсально: тренируйте переключение между разными скоростными режимами")
        if metrics.movement_efficiency < 0.5:
            insights.append("Универсально: работайте над более прямыми и эффективными траекториями")
            
        return insights

def create_scientific_metrics():
    """Фабрика для создания калькулятора научных метрик"""
    return ScientificMetricsCalculator()

# Пример использования
if __name__ == "__main__":
    calculator = create_scientific_calculator()
    interpreter = MetricsInterpreter()
    
    print("🧪 Тестирование ScientificMetricsCalculator...")
    
    # Создаем тестовые данные
    test_positions = []
    for i in range(100):
        x = i * 10 + np.random.normal(0, 5)
        y = 50 * np.sin(i * 0.1) + np.random.normal(0, 2)
        test_positions.append([x, y])
        
    test_positions = np.array(test_positions)
    
    # Рассчитываем метрики
    metrics = calculator.calculate_all_metrics(test_positions)
    
    print("📊 Научные метрики:")
    print(f"   Sample Entropy: {metrics.sample_entropy:.3f}")
    print(f"   Maximum Absolute Deviation: {metrics.maximum_absolute_deviation:.2f}")
    print(f"   Area Under Curve: {metrics.area_under_curve:.2f}")
    print(f"   Bimodality Coefficient: {metrics.bimodality_coefficient:.3f}")
    print(f"   Time to Peak Velocity: {metrics.time_to_peak_velocity:.3f}s")
    print(f"   Movement Efficiency: {metrics.movement_efficiency:.3f}")
    print(f"   Trajectory Complexity: {metrics.trajectory_complexity:.3f}")
    print(f"   Jerk Metric: {metrics.jerk_metric:.2f}")
    
    # Интерпретация
    interpretations = interpreter.interpret_metrics(metrics)
    print("\n🧠 Интерпретация:")
    for metric, interpretation in interpretations.items():
        print(f"   {metric}: {interpretation}")
        
    # Рекомендации для FPS
    fps_insights = interpreter.get_game_specific_insights(metrics, 'tactical_fps')
    print("\n🎯 Рекомендации для FPS:")
    for insight in fps_insights:
        print(f"   • {insight}")