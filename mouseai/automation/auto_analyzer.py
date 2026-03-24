#!/usr/bin/env python3
"""
Auto Analyzer - Автоматический анализ данных
"""

import asyncio
import logging
from typing import Dict, List, Optional, Callable
from datetime import datetime, timedelta
import json
import threading
import time
import numpy as np
from collections import defaultdict

class AutoAnalyzer:
    """Автоматический анализатор данных"""
    
    def __init__(self, mouseai_instance=None):
        self.mouseai = mouseai_instance
        self.logger = logging.getLogger(__name__)
        
        # Конфигурация
        self.config = {
            'enabled': False,
            'analysis_interval': 300,  # Интервал анализа (5 минут)
            'auto_generate_reports': True,
            'trend_analysis': True,
            'anomaly_detection': True,
            'pattern_recognition': True,
            'comparison_analysis': True,
            'predictive_analysis': False,  # Экспериментальная функция
            'report_format': 'json',
            'report_path': 'reports/',
            'min_data_points': 10,  # Минимальное количество точек для анализа
            'sensitivity': 0.1  # Чувствительность детектора аномалий
        }
        
        # Состояние
        self.is_running = False
        self.analysis_results = []
        self.trends = {}
        self.anomalies = []
        self.patterns = []
        
        # Коллбэки
        self.on_analysis_complete = None
        self.on_anomaly_detected = None
        self.on_trend_detected = None
        
        # Потоки
        self.analyzer_thread = None
        
    def configure(self, config: Dict):
        """Настроить анализатор"""
        self.config.update(config)
        self.logger.info(f"Авто-анализ настроен: {config}")
        
    def start(self):
        """Запустить автоматический анализ"""
        if not self.config.get('enabled', False):
            self.logger.warning("Авто-анализ отключен в конфигурации")
            return False
            
        if not self.mouseai:
            self.logger.error("MouseAI не подключен")
            return False
            
        self.is_running = True
        
        # Запускаем поток анализа
        self.analyzer_thread = threading.Thread(target=self._analysis_loop, daemon=True)
        self.analyzer_thread.start()
        
        self.logger.info("Авто-анализ запущен")
        return True
        
    def stop(self):
        """Остановить автоматический анализ"""
        self.is_running = False
        self.logger.info("Авто-анализ остановлен")
        
    def run_manual_analysis(self) -> Dict:
        """Запустить ручной анализ"""
        try:
            # Собираем данные для анализа
            sessions = self.mouseai.get_session_history(100)
            
            if len(sessions) < self.config['min_data_points']:
                self.logger.warning(f"Недостаточно данных для анализа: {len(sessions)}")
                return {'status': 'insufficient_data', 'message': 'Недостаточно данных'}
                
            # Выполняем анализ
            analysis_result = self._perform_analysis(sessions)
            
            self.analysis_results.append(analysis_result)
            
            if self.on_analysis_complete:
                self.on_analysis_complete(analysis_result)
                
            self.logger.info("Ручной анализ завершен")
            return analysis_result
            
        except Exception as e:
            self.logger.error(f"Ошибка ручного анализа: {e}")
            return {'status': 'error', 'message': str(e)}
            
    def _analysis_loop(self):
        """Цикл автоматического анализа"""
        while self.is_running:
            try:
                # Ждем интервал
                time.sleep(self.config['analysis_interval'])
                
                # Проверяем, есть ли новые данные
                sessions = self.mouseai.get_session_history(50)
                
                if len(sessions) >= self.config['min_data_points']:
                    # Выполняем анализ
                    analysis_result = self._perform_analysis(sessions)
                    
                    self.analysis_results.append(analysis_result)
                    
                    # Проверяем аномалии
                    if self.config['anomaly_detection']:
                        anomalies = self._detect_anomalies(sessions)
                        if anomalies:
                            self.anomalies.extend(anomalies)
                            if self.on_anomaly_detected:
                                for anomaly in anomalies:
                                    self.on_anomaly_detected(anomaly)
                                    
                    # Анализируем тренды
                    if self.config['trend_analysis']:
                        trends = self._analyze_trends(sessions)
                        self.trends.update(trends)
                        
                        if self.on_trend_detected:
                            for trend_name, trend_data in trends.items():
                                self.on_trend_detected(trend_name, trend_data)
                                
                    # Распознаем паттерны
                    if self.config['pattern_recognition']:
                        patterns = self._recognize_patterns(sessions)
                        self.patterns.extend(patterns)
                        
                    # Генерируем отчет
                    if self.config['auto_generate_reports']:
                        self._generate_report(analysis_result)
                        
                    if self.on_analysis_complete:
                        self.on_analysis_complete(analysis_result)
                        
            except Exception as e:
                self.logger.error(f"Ошибка в цикле анализа: {e}")
                time.sleep(60)  # Пауза при ошибке
                
    def _perform_analysis(self, sessions: List[Dict]) -> Dict:
        """Выполнить комплексный анализ"""
        result = {
            'timestamp': datetime.now().isoformat(),
            'session_count': len(sessions),
            'analysis_type': 'auto',
            'metrics': {},
            'trends': {},
            'anomalies': [],
            'patterns': [],
            'recommendations': []
        }
        
        # Анализ метрик
        metrics_analysis = self._analyze_metrics(sessions)
        result['metrics'] = metrics_analysis
        
        # Анализ трендов
        if self.config['trend_analysis']:
            trends = self._analyze_trends(sessions)
            result['trends'] = trends
            
        # Детекция аномалий
        if self.config['anomaly_detection']:
            anomalies = self._detect_anomalies(sessions)
            result['anomalies'] = anomalies
            
        # Распознавание паттернов
        if self.config['pattern_recognition']:
            patterns = self._recognize_patterns(sessions)
            result['patterns'] = patterns
            
        # Генерация рекомендаций
        recommendations = self._generate_recommendations(metrics_analysis, trends, anomalies)
        result['recommendations'] = recommendations
        
        return result
        
    def _analyze_metrics(self, sessions: List[Dict]) -> Dict:
        """Анализ метрик"""
        metrics = {
            'sample_entropy': [],
            'maximum_absolute_deviation': [],
            'time_to_peak_velocity': [],
            'movement_efficiency': []
        }
        
        # Собираем данные по метрикам
        for session in sessions:
            session_metrics = session.get('metrics', {})
            for metric_name in metrics.keys():
                if metric_name in session_metrics:
                    metrics[metric_name].append(session_metrics[metric_name])
                    
        # Рассчитываем статистику
        analysis = {}
        for metric_name, values in metrics.items():
            if values:
                analysis[metric_name] = {
                    'mean': np.mean(values),
                    'std': np.std(values),
                    'min': np.min(values),
                    'max': np.max(values),
                    'median': np.median(values),
                    'trend': self._calculate_trend(values)
                }
                
        return analysis
        
    def _calculate_trend(self, values: List[float]) -> str:
        """Рассчитать тренд"""
        if len(values) < 5:
            return 'insufficient_data'
            
        # Простой линейный тренд
        x = np.arange(len(values))
        y = np.array(values)
        
        # Рассчитываем коэффициент корреляции
        correlation = np.corrcoef(x, y)[0, 1]
        
        if np.isnan(correlation):
            return 'no_trend'
        elif correlation > 0.3:
            return 'increasing'
        elif correlation < -0.3:
            return 'decreasing'
        else:
            return 'stable'
            
    def _analyze_trends(self, sessions: List[Dict]) -> Dict:
        """Анализ трендов"""
        trends = {}
        
        # Анализ по играм
        game_trends = defaultdict(list)
        for session in sessions:
            game = session.get('game', 'Unknown')
            metrics = session.get('metrics', {})
            
            for metric_name, value in metrics.items():
                game_trends[f"{game}_{metric_name}"].append(value)
                
        # Определяем тренды
        for metric_key, values in game_trends.items():
            if len(values) >= 10:
                trend = self._calculate_trend(values)
                if trend in ['increasing', 'decreasing']:
                    trends[metric_key] = {
                        'trend': trend,
                        'strength': abs(np.corrcoef(range(len(values)), values)[0, 1]),
                        'values': values[-5:]  # Последние 5 значений
                    }
                    
        return trends
        
    def _detect_anomalies(self, sessions: List[Dict]) -> List[Dict]:
        """Детекция аномалий"""
        anomalies = []
        
        # Анализ по метрикам
        metrics_data = defaultdict(list)
        for session in sessions:
            metrics = session.get('metrics', {})
            for metric_name, value in metrics.items():
                metrics_data[metric_name].append({
                    'value': value,
                    'timestamp': session.get('timestamp'),
                    'game': session.get('game')
                })
                
        # Детекция аномалий для каждой метрики
        for metric_name, data in metrics_data.items():
            if len(data) < 10:
                continue
                
            values = [item['value'] for item in data]
            mean = np.mean(values)
            std = np.std(values)
            
            # Порог аномалии (3 сигмы)
            threshold = self.config['sensitivity'] * std
            
            for item in data:
                if abs(item['value'] - mean) > 3 * std:
                    anomalies.append({
                        'metric': metric_name,
                        'value': item['value'],
                        'expected_range': [mean - 3*std, mean + 3*std],
                        'timestamp': item['timestamp'],
                        'game': item['game'],
                        'severity': 'high' if abs(item['value'] - mean) > 4*std else 'medium'
                    })
                    
        return anomalies
        
    def _recognize_patterns(self, sessions: List[Dict]) -> List[Dict]:
        """Распознавание паттернов"""
        patterns = []
        
        # Анализ по играм
        game_sessions = defaultdict(list)
        for session in sessions:
            game = session.get('game', 'Unknown')
            game_sessions[game].append(session)
            
        # Поиск паттернов для каждой игры
        for game, game_data in game_sessions.items():
            if len(game_data) < 5:
                continue
                
            # Паттерн: улучшение со временем
            efficiency_values = [s.get('metrics', {}).get('movement_efficiency', 0) for s in game_data]
            if len(efficiency_values) >= 5:
                trend = self._calculate_trend(efficiency_values)
                if trend == 'increasing':
                    patterns.append({
                        'type': 'improvement',
                        'game': game,
                        'metric': 'movement_efficiency',
                        'description': f'Улучшение эффективности движений в {game}',
                        'confidence': 0.8
                    })
                    
            # Паттерн: стабильность
            entropy_values = [s.get('metrics', {}).get('sample_entropy', 0) for s in game_data]
            if len(entropy_values) >= 5:
                std = np.std(entropy_values)
                if std < 0.1:  # Низкое стандартное отклонение
                    patterns.append({
                        'type': 'stability',
                        'game': game,
                        'metric': 'sample_entropy',
                        'description': f'Стабильный уровень сложности движений в {game}',
                        'confidence': 0.9
                    })
                    
        return patterns
        
    def _generate_recommendations(self, metrics_analysis: Dict, trends: Dict, anomalies: List[Dict]) -> List[str]:
        """Генерация рекомендаций"""
        recommendations = []
        
        # Рекомендации на основе метрик
        for metric_name, stats in metrics_analysis.items():
            if metric_name == 'sample_entropy':
                if stats['mean'] < 0.3:
                    recommendations.append("Низкий Sample Entropy: Работайте над разнообразием движений")
                elif stats['mean'] > 0.7:
                    recommendations.append("Высокий Sample Entropy: Отличная вариативность движений")
                    
            elif metric_name == 'movement_efficiency':
                if stats['mean'] < 0.5:
                    recommendations.append("Низкая эффективность: Практикуйте более прямые траектории")
                elif stats['mean'] > 0.8:
                    recommendations.append("Высокая эффективность: Отличная точность движений")
                    
        # Рекомендации на основе трендов
        for trend_name, trend_data in trends.items():
            if trend_data['trend'] == 'decreasing':
                recommendations.append(f"Ухудшение {trend_name}: Обратите внимание на эту метрику")
            elif trend_data['trend'] == 'increasing':
                recommendations.append(f"Улучшение {trend_name}: Продолжайте в том же духе")
                
        # Рекомендации на основе аномалий
        for anomaly in anomalies:
            if anomaly['severity'] == 'high':
                recommendations.append(f"Критическая аномалия в {anomaly['metric']}: Проверьте настройки мыши")
                
        # Общие рекомендации
        if not recommendations:
            recommendations.append("Отличные результаты! Продолжайте регулярные тренировки")
            
        return recommendations[:5]  # Ограничиваем количество рекомендаций
        
    def _generate_report(self, analysis_result: Dict):
        """Сгенерировать отчет"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{self.config['report_path']}analysis_report_{timestamp}.{self.config['report_format']}"
            
            # Создаем директорию, если она не существует
            import os
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            if self.config['report_format'] == 'json':
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(analysis_result, f, indent=2, ensure_ascii=False)
            elif self.config['report_format'] == 'txt':
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self._format_text_report(analysis_result))
                    
            self.logger.info(f"Отчет сохранен: {filename}")
            
        except Exception as e:
            self.logger.error(f"Ошибка генерации отчета: {e}")
            
    def _format_text_report(self, analysis_result: Dict) -> str:
        """Форматировать текстовый отчет"""
        report = f"""
MouseAI Автоматический Анализ
{'='*50}

Дата: {analysis_result['timestamp']}
Сессий проанализировано: {analysis_result['session_count']}

Метрики:
{'-'*20}
"""
        
        for metric_name, stats in analysis_result['metrics'].items():
            report += f"{metric_name}:\n"
            report += f"  Среднее: {stats['mean']:.4f}\n"
            report += f"  Стандартное отклонение: {stats['std']:.4f}\n"
            report += f"  Тренд: {stats['trend']}\n\n"
            
        if analysis_result['trends']:
            report += "Тренды:\n"
            report += "-"*20 + "\n"
            for trend_name, trend_data in analysis_result['trends'].items():
                report += f"{trend_name}: {trend_data['trend']} (сила: {trend_data['strength']:.2f})\n"
                
        if analysis_result['anomalies']:
            report += "\nАномалии:\n"
            report += "-"*20 + "\n"
            for anomaly in analysis_result['anomalies']:
                report += f"{anomaly['metric']}: {anomaly['value']:.4f} ({anomaly['severity']})\n"
                
        if analysis_result['recommendations']:
            report += "\nРекомендации:\n"
            report += "-"*20 + "\n"
            for i, rec in enumerate(analysis_result['recommendations'], 1):
                report += f"{i}. {rec}\n"
                
        return report
        
    def get_analysis_status(self) -> Dict:
        """Получить статус анализа"""
        return {
            'enabled': self.config.get('enabled', False),
            'is_running': self.is_running,
            'analysis_count': len(self.analysis_results),
            'anomaly_count': len(self.anomalies),
            'pattern_count': len(self.patterns),
            'last_analysis': self.analysis_results[-1]['timestamp'] if self.analysis_results else None
        }
        
    def get_latest_results(self, limit: int = 5) -> List[Dict]:
        """Получить последние результаты анализа"""
        return self.analysis_results[-limit:]
        
    def get_anomalies(self, limit: int = 10) -> List[Dict]:
        """Получить список аномалий"""
        return self.anomalies[-limit:]
        
    def get_patterns(self, limit: int = 10) -> List[Dict]:
        """Получить список паттернов"""
        return self.patterns[-limit:]
        
    def export_analysis_data(self, filename: str):
        """Экспортировать данные анализа"""
        data = {
            'config': self.config,
            'analysis_results': self.analysis_results,
            'trends': self.trends,
            'anomalies': self.anomalies,
            'patterns': self.patterns
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

def create_auto_analyzer(mouseai_instance=None) -> AutoAnalyzer:
    """Создать автоматический анализатор"""
    return AutoAnalyzer(mouseai_instance)