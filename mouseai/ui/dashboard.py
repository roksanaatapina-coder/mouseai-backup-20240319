#!/usr/bin/env python3
"""
Analysis Dashboard UI - Интерфейс панели анализа
"""

import sys
import os
from pathlib import Path
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
                            QComboBox, QGroupBox, QTabWidget, QWidget, QTextEdit,
                            QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
                            QProgressBar, QCheckBox, QRadioButton, QButtonGroup)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
import logging
import json
from datetime import datetime, timedelta

# Добавляем путь к проекту
sys.path.insert(0, str(Path(__file__).parent.parent))

from mouseai.visualization.dashboard import ProgressDashboard, RealTimeDashboard
from mouseai.utils import MouseAILogger

class AnalysisDashboardDialog(QDialog):
    """Диалог панели анализа"""
    
    def __init__(self, parent=None, mouseai_instance=None):
        super().__init__(parent)
        
        self.mouseai = mouseai_instance
        self.logger = MouseAILogger()
        
        self.setWindowTitle('Панель анализа MouseAI')
        self.setGeometry(200, 200, 1000, 700)
        
        self.dashboard = ProgressDashboard()
        self.live_dashboard = RealTimeDashboard()
        
        self.init_ui()
        self.load_session_data()
        
    def init_ui(self):
        """Инициализация интерфейса"""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Заголовок
        title_label = QLabel('📊 Панель анализа MouseAI')
        title_label.setFont(QFont('Arial', 16, QFont.Bold))
        layout.addWidget(title_label)
        
        # Создаем вкладки
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # Вкладки
        self.create_overview_tab()
        self.create_metrics_tab()
        self.create_progress_tab()
        self.create_comparison_tab()
        self.create_live_tab()
        
        # Кнопки управления
        btn_layout = QHBoxLayout()
        
        refresh_btn = QPushButton('Обновить данные')
        refresh_btn.clicked.connect(self.refresh_data)
        btn_layout.addWidget(refresh_btn)
        
        export_btn = QPushButton('Экспортировать отчет')
        export_btn.clicked.connect(self.export_report)
        btn_layout.addWidget(export_btn)
        
        close_btn = QPushButton('Закрыть')
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
        
    def create_overview_tab(self):
        """Создать вкладку обзора"""
        overview_widget = QWidget()
        layout = QVBoxLayout()
        overview_widget.setLayout(layout)
        
        # Группа общих показателей
        stats_group = QGroupBox('Общие показатели')
        stats_layout = QVBoxLayout()
        stats_group.setLayout(stats_layout)
        
        # Статистика
        self.stats_table = QTableWidget()
        self.stats_table.setColumnCount(2)
        self.stats_table.setHorizontalHeaderLabels(['Показатель', 'Значение'])
        self.stats_table.horizontalHeader().setStretchLastSection(True)
        self.stats_table.verticalHeader().setVisible(False)
        stats_layout.addWidget(self.stats_table)
        
        layout.addWidget(stats_group)
        
        # Группа рекомендаций
        recommendations_group = QGroupBox('Рекомендации')
        recommendations_layout = QVBoxLayout()
        recommendations_group.setLayout(recommendations_layout)
        
        self.recommendations_text = QTextEdit()
        self.recommendations_text.setReadOnly(True)
        recommendations_layout.addWidget(self.recommendations_text)
        
        layout.addWidget(recommendations_group)
        
        self.tabs.addTab(overview_widget, 'Обзор')
        
    def create_metrics_tab(self):
        """Создать вкладку метрик"""
        metrics_widget = QWidget()
        layout = QVBoxLayout()
        metrics_widget.setLayout(layout)
        
        # Группа текущих метрик
        current_metrics_group = QGroupBox('Текущие метрики')
        current_layout = QVBoxLayout()
        current_metrics_group.setLayout(current_layout)
        
        self.current_metrics_table = QTableWidget()
        self.current_metrics_table.setColumnCount(2)
        self.current_metrics_table.setHorizontalHeaderLabels(['Метрика', 'Значение'])
        self.current_metrics_table.horizontalHeader().setStretchLastSection(True)
        self.current_metrics_table.verticalHeader().setVisible(False)
        current_layout.addWidget(self.current_metrics_table)
        
        layout.addWidget(current_metrics_group)
        
        # Группа исторических метрик
        history_metrics_group = QGroupBox('История метрик')
        history_layout = QVBoxLayout()
        history_metrics_group.setLayout(history_layout)
        
        self.history_metrics_table = QTableWidget()
        self.history_metrics_table.setColumnCount(6)
        self.history_metrics_table.setHorizontalHeaderLabels(['Дата', 'Игра', 'Sample Entropy', 'MAD', 'TTPV', 'Efficiency'])
        self.history_metrics_table.horizontalHeader().setStretchLastSection(True)
        self.history_metrics_table.verticalHeader().setVisible(False)
        history_layout.addWidget(self.history_metrics_table)
        
        layout.addWidget(history_metrics_group)
        
        self.tabs.addTab(metrics_widget, 'Метрики')
        
    def create_progress_tab(self):
        """Создать вкладку прогресса"""
        progress_widget = QWidget()
        layout = QVBoxLayout()
        progress_widget.setLayout(layout)
        
        # Группа прогресса
        progress_group = QGroupBox('Прогресс')
        progress_layout = QVBoxLayout()
        progress_group.setLayout(progress_layout)
        
        # Прогресс бары
        progress_items = [
            ('Sample Entropy', 'sample_entropy_progress'),
            ('Movement Efficiency', 'efficiency_progress'),
            ('Reaction Time', 'reaction_progress'),
            ('Accuracy', 'accuracy_progress')
        ]
        
        for label, attr_name in progress_items:
            item_layout = QHBoxLayout()
            item_layout.addWidget(QLabel(label))
            
            progress_bar = QProgressBar()
            progress_bar.setRange(0, 100)
            progress_bar.setValue(0)
            item_layout.addWidget(progress_bar)
            
            setattr(self, attr_name, progress_bar)
            progress_layout.addLayout(item_layout)
            
        layout.addWidget(progress_group)
        
        # Группа целей
        goals_group = QGroupBox('Цели')
        goals_layout = QVBoxLayout()
        goals_group.setLayout(goals_layout)
        
        self.goals_text = QTextEdit()
        self.goals_text.setReadOnly(True)
        goals_layout.addWidget(self.goals_text)
        
        layout.addWidget(goals_group)
        
        self.tabs.addTab(progress_widget, 'Прогресс')
        
    def create_comparison_tab(self):
        """Создать вкладку сравнения"""
        comparison_widget = QWidget()
        layout = QVBoxLayout()
        comparison_widget.setLayout(layout)
        
        # Группа сравнения с нормами
        norms_group = QGroupBox('Сравнение с нормами')
        norms_layout = QVBoxLayout()
        norms_group.setLayout(norms_layout)
        
        self.norms_table = QTableWidget()
        self.norms_table.setColumnCount(3)
        self.norms_table.setHorizontalHeaderLabels(['Метрика', 'Ваш результат', 'Норма'])
        self.norms_table.horizontalHeader().setStretchLastSection(True)
        self.norms_table.verticalHeader().setVisible(False)
        norms_layout.addWidget(self.norms_table)
        
        layout.addWidget(norms_group)
        
        # Группа сравнения с прошлыми сессиями
        history_group = QGroupBox('Сравнение с прошлыми сессиями')
        history_layout = QVBoxLayout()
        history_group.setLayout(history_layout)
        
        self.history_comparison_table = QTableWidget()
        self.history_comparison_table.setColumnCount(4)
        self.history_comparison_table.setHorizontalHeaderLabels(['Сессия', 'Sample Entropy', 'Efficiency', 'Улучшение'])
        self.history_comparison_table.horizontalHeader().setStretchLastSection(True)
        self.history_comparison_table.verticalHeader().setVisible(False)
        history_layout.addWidget(self.history_comparison_table)
        
        layout.addWidget(history_group)
        
        self.tabs.addTab(comparison_widget, 'Сравнение')
        
    def create_live_tab(self):
        """Создать вкладку реального времени"""
        live_widget = QWidget()
        layout = QVBoxLayout()
        live_widget.setLayout(layout)
        
        # Группа live метрик
        live_group = QGroupBox('Live метрики')
        live_layout = QVBoxLayout()
        live_group.setLayout(live_layout)
        
        # Live прогресс бары
        live_items = [
            ('Текущая скорость', 'live_speed_progress'),
            ('Средняя скорость', 'live_avg_speed_progress'),
            ('Максимальная скорость', 'live_max_speed_progress'),
            ('Длительность сессии', 'live_duration_progress')
        ]
        
        for label, attr_name in live_items:
            item_layout = QHBoxLayout()
            item_layout.addWidget(QLabel(label))
            
            progress_bar = QProgressBar()
            progress_bar.setRange(0, 100)
            progress_bar.setValue(0)
            item_layout.addWidget(progress_bar)
            
            setattr(self, attr_name, progress_bar)
            live_layout.addLayout(item_layout)
            
        layout.addWidget(live_group)
        
        # Группа live статуса
        status_group = QGroupBox('Live статус')
        status_layout = QVBoxLayout()
        status_group.setLayout(status_layout)
        
        self.live_status_text = QTextEdit()
        self.live_status_text.setReadOnly(True)
        self.live_status_text.setMaximumHeight(100)
        status_layout.addWidget(self.live_status_text)
        
        layout.addWidget(status_group)
        
        # Кнопки управления live
        live_btn_layout = QHBoxLayout()
        
        start_live_btn = QPushButton('Начать live мониторинг')
        start_live_btn.clicked.connect(self.start_live_monitoring)
        live_btn_layout.addWidget(start_live_btn)
        
        stop_live_btn = QPushButton('Остановить live мониторинг')
        stop_live_btn.clicked.connect(self.stop_live_monitoring)
        live_btn_layout.addWidget(stop_live_btn)
        
        layout.addLayout(live_btn_layout)
        
        self.tabs.addTab(live_widget, 'Live')
        
        # Таймер для live обновления
        self.live_timer = QTimer()
        self.live_timer.timeout.connect(self.update_live_data)
        
    def load_session_data(self):
        """Загрузить данные сессий"""
        try:
            if self.mouseai:
                sessions = self.mouseai.get_session_history(50)
                
                for session in sessions:
                    self.dashboard.add_session(session)
                    
                self.update_overview()
                self.update_metrics()
                self.update_progress()
                self.update_comparison()
                
        except Exception as e:
            self.logger.error(f"Ошибка загрузки данных сессий: {e}")
            
    def update_overview(self):
        """Обновить обзор"""
        try:
            # Обновляем статистику
            stats = self.calculate_stats()
            
            self.stats_table.setRowCount(len(stats))
            
            for row, (key, value) in enumerate(stats.items()):
                key_item = QTableWidgetItem(key)
                value_item = QTableWidgetItem(str(value))
                
                self.stats_table.setItem(row, 0, key_item)
                self.stats_table.setItem(row, 1, value_item)
                
            self.stats_table.resizeColumnsToContents()
            
            # Обновляем рекомендации
            recommendations = self.generate_recommendations(stats)
            self.recommendations_text.setText(recommendations)
            
        except Exception as e:
            self.logger.error(f"Ошибка обновления обзора: {e}")
            
    def update_metrics(self):
        """Обновить метрики"""
        try:
            # Обновляем текущие метрики
            if self.mouseai:
                current_metrics = self.mouseai.get_current_metrics()
                
                if current_metrics:
                    self.current_metrics_table.setRowCount(len(current_metrics))
                    
                    row = 0
                    for key, value in current_metrics.items():
                        metric_item = QTableWidgetItem(key.replace('_', ' ').title())
                        value_item = QTableWidgetItem(f"{value:.4f}" if isinstance(value, float) else str(value))
                        
                        self.current_metrics_table.setItem(row, 0, metric_item)
                        self.current_metrics_table.setItem(row, 1, value_item)
                        row += 1
                        
                    self.current_metrics_table.resizeColumnsToContents()
                    
            # Обновляем историю метрик
            sessions = self.dashboard.session_history
            
            self.history_metrics_table.setRowCount(len(sessions))
            
            for row, session in enumerate(sessions):
                date_item = QTableWidgetItem(session.get('timestamp', '').strftime('%Y-%m-%d %H:%M'))
                game_item = QTableWidgetItem(session.get('game', ''))
                
                metrics = session.get('metrics', {})
                entropy_item = QTableWidgetItem(f"{metrics.get('sample_entropy', 0):.4f}")
                mad_item = QTableWidgetItem(f"{metrics.get('maximum_absolute_deviation', 0):.2f}")
                ttpv_item = QTableWidgetItem(f"{metrics.get('time_to_peak_velocity', 0):.3f}")
                efficiency_item = QTableWidgetItem(f"{metrics.get('movement_efficiency', 0):.3f}")
                
                self.history_metrics_table.setItem(row, 0, date_item)
                self.history_metrics_table.setItem(row, 1, game_item)
                self.history_metrics_table.setItem(row, 2, entropy_item)
                self.history_metrics_table.setItem(row, 3, mad_item)
                self.history_metrics_table.setItem(row, 4, ttpv_item)
                self.history_metrics_table.setItem(row, 5, efficiency_item)
                
            self.history_metrics_table.resizeColumnsToContents()
            
        except Exception as e:
            self.logger.error(f"Ошибка обновления метрик: {e}")
            
    def update_progress(self):
        """Обновить прогресс"""
        try:
            # Рассчитываем прогресс по метрикам
            if self.dashboard.player_stats and self.dashboard.player_stats['session_count'] > 0:
                stats = self.dashboard.player_stats
                
                # Sample Entropy прогресс (чем выше, тем лучше)
                avg_entropy = sum(stats['avg_sample_entropy']) / len(stats['avg_sample_entropy'])
                entropy_progress = min(100, int(avg_entropy * 100))
                self.sample_entropy_progress.setValue(entropy_progress)
                
                # Efficiency прогресс (чем выше, тем лучше)
                avg_efficiency = sum(stats['avg_efficiency']) / len(stats['avg_efficiency'])
                efficiency_progress = min(100, int(avg_efficiency * 100))
                self.efficiency_progress.setValue(efficiency_progress)
                
                # Reaction Time прогресс (чем ниже TTPV, тем лучше)
                avg_ttpv = sum(stats['avg_ttpv']) / len(stats['avg_ttpv'])
                reaction_progress = max(0, 100 - int(avg_ttpv * 200))  # Инвертируем
                self.reaction_progress.setValue(reaction_progress)
                
                # Accuracy прогресс (чем ниже MAD, тем лучше)
                avg_mad = sum(stats['avg_mad']) / len(stats['avg_mad'])
                accuracy_progress = max(0, 100 - int(avg_mad / 10))  # Инвертируем
                self.accuracy_progress.setValue(accuracy_progress)
                
            # Обновляем цели
            goals = self.generate_goals()
            self.goals_text.setText(goals)
            
        except Exception as e:
            self.logger.error(f"Ошибка обновления прогресса: {e}")
            
    def update_comparison(self):
        """Обновить сравнение"""
        try:
            # Сравнение с нормами
            current_metrics = {}
            if self.mouseai:
                current_metrics = self.mouseai.get_current_metrics()
                
            norms = self.get_norms()
            
            self.norms_table.setRowCount(len(norms))
            
            row = 0
            for metric, norm_value in norms.items():
                metric_item = QTableWidgetItem(metric.replace('_', ' ').title())
                
                current_value = current_metrics.get(metric, 0)
                current_item = QTableWidgetItem(f"{current_value:.4f}" if isinstance(current_value, float) else str(current_value))
                
                norm_item = QTableWidgetItem(f"{norm_value:.4f}")
                
                self.norms_table.setItem(row, 0, metric_item)
                self.norms_table.setItem(row, 1, current_item)
                self.norms_table.setItem(row, 2, norm_item)
                row += 1
                
            self.norms_table.resizeColumnsToContents()
            
            # Сравнение с прошлыми сессиями
            sessions = self.dashboard.session_history[-10:]  # Последние 10 сессий
            
            self.history_comparison_table.setRowCount(len(sessions))
            
            for row, session in enumerate(sessions):
                session_item = QTableWidgetItem(session.get('timestamp', '').strftime('%Y-%m-%d %H:%M'))
                
                metrics = session.get('metrics', {})
                entropy_item = QTableWidgetItem(f"{metrics.get('sample_entropy', 0):.4f}")
                efficiency_item = QTableWidgetItem(f"{metrics.get('movement_efficiency', 0):.3f}")
                
                # Рассчитываем улучшение (простое сравнение с предыдущей сессией)
                improvement = "Нет данных"
                if row > 0:
                    prev_session = sessions[row-1]
                    prev_metrics = prev_session.get('metrics', {})
                    prev_entropy = prev_metrics.get('sample_entropy', 0)
                    prev_efficiency = prev_metrics.get('movement_efficiency', 0)
                    
                    entropy_change = metrics.get('sample_entropy', 0) - prev_entropy
                    efficiency_change = metrics.get('movement_efficiency', 0) - prev_efficiency
                    
                    if entropy_change > 0 and efficiency_change > 0:
                        improvement = "Улучшение"
                    elif entropy_change < 0 and efficiency_change < 0:
                        improvement = "Ухудшение"
                    else:
                        improvement = "Стабильно"
                        
                improvement_item = QTableWidgetItem(improvement)
                
                self.history_comparison_table.setItem(row, 0, session_item)
                self.history_comparison_table.setItem(row, 1, entropy_item)
                self.history_comparison_table.setItem(row, 2, efficiency_item)
                self.history_comparison_table.setItem(row, 3, improvement_item)
                
            self.history_comparison_table.resizeColumnsToContents()
            
        except Exception as e:
            self.logger.error(f"Ошибка обновления сравнения: {e}")
            
    def calculate_stats(self):
        """Рассчитать статистику"""
        stats = {}
        
        if self.dashboard.player_stats and self.dashboard.player_stats['session_count'] > 0:
            stats['Всего сессий'] = self.dashboard.player_stats['session_count']
            
            # Средние значения
            if self.dashboard.player_stats['avg_sample_entropy']:
                stats['Средний Sample Entropy'] = f"{sum(self.dashboard.player_stats['avg_sample_entropy']) / len(self.dashboard.player_stats['avg_sample_entropy']):.4f}"
                
            if self.dashboard.player_stats['avg_efficiency']:
                stats['Средняя эффективность'] = f"{sum(self.dashboard.player_stats['avg_efficiency']) / len(self.dashboard.player_stats['avg_efficiency']):.3f}"
                
            if self.dashboard.player_stats['avg_ttpv']:
                stats['Среднее TTPV'] = f"{sum(self.dashboard.player_stats['avg_ttpv']) / len(self.dashboard.player_stats['avg_ttpv']):.3f}"
                
            # Самые популярные игры
            game_stats = {}
            for session in self.dashboard.session_history:
                game = session.get('game', 'Unknown')
                if game not in game_stats:
                    game_stats[game] = 0
                game_stats[game] += 1
                
            if game_stats:
                most_popular = max(game_stats, key=game_stats.get)
                stats['Самая популярная игра'] = f"{most_popular} ({game_stats[most_popular]} сессий)"
                
        return stats
        
    def generate_recommendations(self, stats):
        """Сгенерировать рекомендации"""
        recommendations = []
        
        # Анализ по метрикам
        if 'Средний Sample Entropy' in stats:
            entropy = float(stats['Средний Sample Entropy'])
            if entropy < 0.3:
                recommendations.append("• Низкий Sample Entropy: Работайте над разнообразием движений")
            elif entropy > 0.7:
                recommendations.append("• Высокий Sample Entropy: Отличная вариативность движений")
                
        if 'Средняя эффективность' in stats:
            efficiency = float(stats['Средняя эффективность'])
            if efficiency < 0.5:
                recommendations.append("• Низкая эффективность: Практикуйте более прямые траектории")
            elif efficiency > 0.8:
                recommendations.append("• Высокая эффективность: Отличная точность движений")
                
        # Рекомендации по играм
        if 'Самая популярная игра' in stats:
            recommendations.append(f"• Продолжайте тренировки в {stats['Самая популярная игра']}")
            
        recommendations.append("• Регулярно проходите сессии анализа")
        recommendations.append("• Следите за прогрессом в динамике")
        recommendations.append("• Используйте рекомендации для улучшения навыков")
        
        return "\n".join(recommendations)
        
    def generate_goals(self):
        """Сгенерировать цели"""
        goals = []
        
        if self.dashboard.player_stats and self.dashboard.player_stats['session_count'] > 0:
            current_entropy = sum(self.dashboard.player_stats['avg_sample_entropy']) / len(self.dashboard.player_stats['avg_sample_entropy'])
            current_efficiency = sum(self.dashboard.player_stats['avg_efficiency']) / len(self.dashboard.player_stats['avg_efficiency'])
            
            goals.append(f"• Увеличить Sample Entropy до {current_entropy + 0.1:.3f}")
            goals.append(f"• Повысить эффективность до {current_efficiency + 0.1:.3f}")
            goals.append("• Пройти 10 сессий анализа")
            goals.append("• Достичь стабильных результатов")
            
        return "\n".join(goals)
        
    def get_norms(self):
        """Получить нормы для метрик"""
        return {
            'sample_entropy': 0.5,
            'maximum_absolute_deviation': 50.0,
            'time_to_peak_velocity': 0.2,
            'movement_efficiency': 0.7
        }
        
    def start_live_monitoring(self):
        """Начать live мониторинг"""
        self.live_timer.start(1000)  # Обновление каждую секунду
        self.live_status_text.setText("Live мониторинг активен")
        
    def stop_live_monitoring(self):
        """Остановить live мониторинг"""
        self.live_timer.stop()
        self.live_status_text.setText("Live мониторинг остановлен")
        
    def update_live_data(self):
        """Обновить live данные"""
        try:
            if self.mouseai:
                # Получаем текущие live метрики
                current_metrics = self.mouseai.get_current_metrics()
                
                if current_metrics:
                    # Обновляем live прогресс бары
                    if 'sample_entropy' in current_metrics:
                        entropy = current_metrics['sample_entropy']
                        self.live_speed_progress.setValue(int(entropy * 100))
                        
                    if 'movement_efficiency' in current_metrics:
                        efficiency = current_metrics['movement_efficiency']
                        self.live_avg_speed_progress.setValue(int(efficiency * 100))
                        
                    # Обновляем статус
                    status = self.mouseai.get_status()
                    status_text = f"Игра: {status.get('current_game', 'Нет')}\n"
                    status_text += f"Стиль: {status.get('current_style', 'Не определен')}\n"
                    status_text += f"Длительность: {status.get('session_duration', 0)} сек"
                    
                    self.live_status_text.setText(status_text)
                    
        except Exception as e:
            self.logger.error(f"Ошибка обновления live данных: {e}")
            
    def refresh_data(self):
        """Обновить данные"""
        self.load_session_data()
        QMessageBox.information(self, 'Обновление', 'Данные обновлены')
        
    def export_report(self):
        """Экспортировать отчет"""
        try:
            # Генерируем отчет
            report_data = {
                'timestamp': datetime.now().isoformat(),
                'overview': self.calculate_stats(),
                'recommendations': self.generate_recommendations(self.calculate_stats()),
                'goals': self.generate_goals(),
                'norms': self.get_norms()
            }
            
            # Сохраняем в файл
            filename = f"mouseai_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
                
            QMessageBox.information(self, 'Экспорт', f'Отчет экспортирован в {filename}')
            
        except Exception as e:
            self.logger.error(f"Ошибка экспорта отчета: {e}")
            QMessageBox.critical(self, 'Ошибка', f'Не удалось экспортировать отчет: {e}')

def create_analysis_dashboard(parent=None, mouseai_instance=None) -> AnalysisDashboardDialog:
    """Создать панель анализа"""
    return AnalysisDashboardDialog(parent, mouseai_instance)