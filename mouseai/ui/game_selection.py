#!/usr/bin/env python3
"""
Game Selection UI - Интерфейс выбора игры
"""

import sys
import os
from pathlib import Path
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
                            QComboBox, QGroupBox, QRadioButton, QButtonGroup, QCheckBox,
                            QSpinBox, QDoubleSpinBox, QTabWidget, QWidget, QTextEdit,
                            QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
import logging

# Добавляем путь к проекту
sys.path.insert(0, str(Path(__file__).parent.parent))

# from mouseai.core import MouseAI
from mouseai.utils import MouseAILogger

class GameSelectionDialog(QDialog):
    """Диалог выбора игры"""
    
    game_selected = pyqtSignal(str, dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # self.mouseai = MouseAI()
        self.logger = MouseAILogger()
        
        self.setWindowTitle('Выбор игры для анализа')
        self.setGeometry(200, 200, 600, 500)
        
        self.init_ui()
        
    def init_ui(self):
        """Инициализация интерфейса"""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Заголовок
        title_label = QLabel('Настройка сессии анализа')
        title_label.setFont(QFont('Arial', 16, QFont.Bold))
        layout.addWidget(title_label)
        
        # Создаем вкладки
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # Вкладки
        self.create_game_tab()
        self.create_advanced_tab()
        self.create_preview_tab()
        
        # Кнопки управления
        btn_layout = QHBoxLayout()
        
        self.start_btn = QPushButton('Начать анализ')
        self.start_btn.clicked.connect(self.start_analysis)
        self.start_btn.setStyleSheet('background-color: green; color: white; font-weight: bold;')
        btn_layout.addWidget(self.start_btn)
        
        cancel_btn = QPushButton('Отмена')
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
        
    def create_game_tab(self):
        """Создать вкладку выбора игры"""
        game_widget = QWidget()
        layout = QVBoxLayout()
        game_widget.setLayout(layout)
        
        # Группа выбора игры
        game_group = QGroupBox('Выбор игры')
        game_layout = QVBoxLayout()
        game_group.setLayout(game_layout)
        
        # Список игр
        self.game_combo = QComboBox()
        games = [
            'CS2 (Counter-Strike 2)',
            'PUBG (PlayerUnknown\'s Battlegrounds)',
            'Valorant',
            'Overwatch 2',
            'Rainbow Six Siege',
            'Call of Duty: Warzone',
            'Fortnite',
            'Apex Legends',
            'Escape from Tarkov',
            'Rainbow Six Extraction'
        ]
        self.game_combo.addItems(games)
        game_layout.addWidget(QLabel('Игра:'))
        game_layout.addWidget(self.game_combo)
        
        # Описание игры
        self.game_description = QTextEdit()
        self.game_description.setReadOnly(True)
        self.game_description.setMaximumHeight(100)
        game_layout.addWidget(QLabel('Описание:'))
        game_layout.addWidget(self.game_description)
        
        layout.addWidget(game_group)
        
        # Группа настроек сессии
        session_group = QGroupBox('Настройки сессии')
        session_layout = QVBoxLayout()
        session_group.setLayout(session_layout)
        
        # Длительность
        duration_layout = QHBoxLayout()
        duration_layout.addWidget(QLabel('Длительность (сек):'))
        self.duration_spin = QSpinBox()
        self.duration_spin.setRange(30, 3600)
        self.duration_spin.setValue(300)
        self.duration_spin.valueChanged.connect(self.update_session_info)
        duration_layout.addWidget(self.duration_spin)
        session_layout.addLayout(duration_layout)
        
        # Тип анализа
        analysis_layout = QHBoxLayout()
        analysis_layout.addWidget(QLabel('Тип анализа:'))
        self.analysis_group = QButtonGroup()
        
        quick_radio = QRadioButton('Быстрый (2-5 мин)')
        detailed_radio = QRadioButton('Подробный (10-30 мин)')
        pro_radio = QRadioButton('Профессиональный (30+ мин)')
        
        self.analysis_group.addButton(quick_radio, 1)
        self.analysis_group.addButton(detailed_radio, 2)
        self.analysis_group.addButton(pro_radio, 3)
        
        quick_radio.setChecked(True)
        quick_radio.toggled.connect(self.update_analysis_settings)
        
        analysis_layout.addWidget(quick_radio)
        analysis_layout.addWidget(detailed_radio)
        analysis_layout.addWidget(pro_radio)
        session_layout.addLayout(analysis_layout)
        
        # Цель анализа
        goal_layout = QHBoxLayout()
        goal_layout.addWidget(QLabel('Цель анализа:'))
        self.goal_combo = QComboBox()
        self.goal_combo.addItems([
            'Общее улучшение',
            'Улучшение реакции',
            'Улучшение точности',
            'Анализ стиля игры',
            'Подготовка к турнирам'
        ])
        goal_layout.addWidget(self.goal_combo)
        session_layout.addLayout(goal_layout)
        
        layout.addWidget(session_group)
        
        # Информация о сессии
        self.session_info = QTextEdit()
        self.session_info.setReadOnly(True)
        self.session_info.setMaximumHeight(80)
        layout.addWidget(QLabel('Информация о сессии:'))
        layout.addWidget(self.session_info)
        
        self.tabs.addTab(game_widget, 'Игра')
        
        # Обновляем информацию
        self.update_game_description()
        self.update_session_info()
        
    def create_advanced_tab(self):
        """Создать вкладку продвинутых настроек"""
        advanced_widget = QWidget()
        layout = QVBoxLayout()
        advanced_widget.setLayout(layout)
        
        # Группа настроек сбора данных
        data_group = QGroupBox('Настройки сбора данных')
        data_layout = QVBoxLayout()
        data_group.setLayout(data_layout)
        
        # Частота сбора
        freq_layout = QHBoxLayout()
        freq_layout.addWidget(QLabel('Частота сбора (Гц):'))
        self.freq_spin = QSpinBox()
        self.freq_spin.setRange(60, 1000)
        self.freq_spin.setValue(120)
        freq_layout.addWidget(self.freq_spin)
        data_layout.addLayout(freq_layout)
        
        # Фильтрация
        self.filter_checkbox = QCheckBox('Включить фильтрацию шума')
        self.filter_checkbox.setChecked(True)
        data_layout.addWidget(self.filter_checkbox)
        
        # Сглаживание
        smooth_layout = QHBoxLayout()
        smooth_layout.addWidget(QLabel('Сглаживание:'))
        self.smooth_spin = QDoubleSpinBox()
        self.smooth_spin.setRange(0.1, 1.0)
        self.smooth_spin.setValue(0.5)
        self.smooth_spin.setSingleStep(0.1)
        smooth_layout.addWidget(self.smooth_spin)
        data_layout.addLayout(smooth_layout)
        
        layout.addWidget(data_group)
        
        # Группа настроек анализа
        analysis_group = QGroupBox('Настройки анализа')
        analysis_layout = QVBoxLayout()
        analysis_group.setLayout(analysis_layout)
        
        # Метод анализа
        method_layout = QHBoxLayout()
        method_layout.addWidget(QLabel('Метод анализа:'))
        self.method_combo = QComboBox()
        self.method_combo.addItems([
            'Научный (классический)',
            'Машинное обучение',
            'Комбинированный',
            'Экспертный'
        ])
        method_layout.addWidget(self.method_combo)
        analysis_layout.addLayout(method_layout)
        
        # Точность анализа
        accuracy_layout = QHBoxLayout()
        accuracy_layout.addWidget(QLabel('Точность анализа:'))
        self.accuracy_group = QButtonGroup()
        
        low_radio = QRadioButton('Низкая')
        medium_radio = QRadioButton('Средняя')
        high_radio = QRadioButton('Высокая')
        ultra_radio = QRadioButton('Ультра')
        
        self.accuracy_group.addButton(low_radio, 1)
        self.accuracy_group.addButton(medium_radio, 2)
        self.accuracy_group.addButton(high_radio, 3)
        self.accuracy_group.addButton(ultra_radio, 4)
        
        medium_radio.setChecked(True)
        
        accuracy_layout.addWidget(low_radio)
        accuracy_layout.addWidget(medium_radio)
        accuracy_layout.addWidget(high_radio)
        accuracy_layout.addWidget(ultra_radio)
        analysis_layout.addLayout(accuracy_layout)
        
        layout.addWidget(analysis_group)
        
        # Группа метрик
        metrics_group = QGroupBox('Метрики для анализа')
        metrics_layout = QVBoxLayout()
        metrics_group.setLayout(metrics_layout)
        
        self.metrics_checkboxes = {}
        metrics = [
            ('sample_entropy', 'Sample Entropy (Сложность движений)'),
            ('maximum_absolute_deviation', 'MAD (Точность)'),
            ('time_to_peak_velocity', 'TTPV (Реакция)'),
            ('movement_efficiency', 'Efficiency (Эффективность)'),
            ('jerk_metrics', 'Jerk Metrics (Плавность)'),
            ('frequency_analysis', 'Frequency Analysis (Частотный анализ)'),
            ('biomechanical_metrics', 'Biomechanical (Биомеханика)')
        ]
        
        for metric_key, metric_name in metrics:
            checkbox = QCheckBox(metric_name)
            checkbox.setChecked(True)  # По умолчанию все включено
            self.metrics_checkboxes[metric_key] = checkbox
            metrics_layout.addWidget(checkbox)
            
        layout.addWidget(metrics_group)
        
        self.tabs.addTab(advanced_widget, 'Настройки')
        
    def create_preview_tab(self):
        """Создать вкладку предварительного просмотра"""
        preview_widget = QWidget()
        layout = QVBoxLayout()
        preview_widget.setLayout(layout)
        
        # Таблица рекомендаций
        self.recommendations_table = QTableWidget()
        self.recommendations_table.setColumnCount(2)
        self.recommendations_table.setHorizontalHeaderLabels(['Параметр', 'Рекомендация'])
        self.recommendations_table.horizontalHeader().setStretchLastSection(True)
        self.recommendations_table.verticalHeader().setVisible(False)
        layout.addWidget(QLabel('Рекомендации для выбранной игры:'))
        layout.addWidget(self.recommendations_table)
        
        # Советы
        self.tips_text = QTextEdit()
        self.tips_text.setReadOnly(True)
        layout.addWidget(QLabel('Советы по проведению сессии:'))
        layout.addWidget(self.tips_text)
        
        self.tabs.addTab(preview_widget, 'Предпросмотр')
        
        # Обновляем рекомендации
        self.update_recommendations()
        
    def update_game_description(self):
        """Обновить описание игры"""
        game = self.game_combo.currentText()
        
        descriptions = {
            'CS2 (Counter-Strike 2)': 'Шутер от первого лица с командной игрой. Требует высокой точности и быстрой реакции.',
            'PUBG (PlayerUnknown\'s Battlegrounds)': 'Баттл-рояль с элементами тактики. Важна точность и стратегическое мышление.',
            'Valorant': 'Тактический шутер с уникальными способностями. Требует сочетания реакции и стратегии.',
            'Overwatch 2': 'Командный шутер с разнообразными героями. Важна адаптивность и командная игра.',
            'Rainbow Six Siege': 'Тактический шутер с разрушаемой средой. Требует точности и стратегического мышления.',
            'Call of Duty: Warzone': 'Баттл-рояль с быстрым темпом. Важна реакция и адаптивность.',
            'Fortnite': 'Баттл-рояль с элементами строительства. Требует многозадачности и реакции.',
            'Apex Legends': 'Баттл-рояль с уникальными героями. Важна командная игра и реакция.',
            'Escape from Tarkov': 'Хардкорный шутер с реалистичной баллистикой. Требует высокой точности.',
            'Rainbow Six Extraction': 'Кооперативный тактический шутер. Важна точность и командная работа.'
        }
        
        description = descriptions.get(game, 'Описание недоступно.')
        self.game_description.setText(description)
        
    def update_session_info(self):
        """Обновить информацию о сессии"""
        duration = self.duration_spin.value()
        analysis_type = self.analysis_group.checkedId()
        
        info = f"Длительность сессии: {duration} секунд\n"
        
        if analysis_type == 1:  # Быстрый
            info += "Тип анализа: Быстрый (2-5 минут)\n"
            info += "Подходит для быстрой оценки текущего состояния."
        elif analysis_type == 2:  # Подробный
            info += "Тип анализа: Подробный (10-30 минут)\n"
            info += "Предоставляет детальную информацию о стиле игры."
        elif analysis_type == 3:  # Профессиональный
            info += "Тип анализа: Профессиональный (30+ минут)\n"
            info += "Полный анализ для профессиональных игроков."
            
        self.session_info.setText(info)
        
    def update_analysis_settings(self):
        """Обновить настройки анализа"""
        analysis_type = self.analysis_group.checkedId()
        
        if analysis_type == 1:  # Быстрый
            self.duration_spin.setValue(300)  # 5 минут
            self.freq_spin.setValue(120)
            self.method_combo.setCurrentText('Научный (классический)')
            self.accuracy_group.button(1).setChecked(True)  # Низкая
        elif analysis_type == 2:  # Подробный
            self.duration_spin.setValue(900)  # 15 минут
            self.freq_spin.setValue(240)
            self.method_combo.setCurrentText('Комбинированный')
            self.accuracy_group.button(2).setChecked(True)  # Средняя
        elif analysis_type == 3:  # Профессиональный
            self.duration_spin.setValue(1800)  # 30 минут
            self.freq_spin.setValue(500)
            self.method_combo.setCurrentText('Экспертный')
            self.accuracy_group.button(4).setChecked(True)  # Ультра
            
        self.update_session_info()
        self.update_recommendations()
        
    def update_recommendations(self):
        """Обновить рекомендации"""
        game = self.game_combo.currentText()
        duration = self.duration_spin.value()
        
        # Очищаем таблицу
        self.recommendations_table.setRowCount(0)
        
        recommendations = []
        
        if 'CS2' in game:
            recommendations.extend([
                ('Длительность', f'{duration} сек - оптимально для CS2'),
                ('Частота сбора', '120-240 Гц для точного анализа'),
                ('Фокус', 'Точность и время реакции'),
                ('Совет', 'Используйте aim-тренировки для улучшения')
            ])
        elif 'PUBG' in game:
            recommendations.extend([
                ('Длительность', f'{duration} сек - подходит для PUBG'),
                ('Частота сбора', '60-120 Гц для стабильного анализа'),
                ('Фокус', 'Точность и стратегическое мышление'),
                ('Совет', 'Тренируйте прицеливание на разных дистанциях')
            ])
        elif 'Valorant' in game:
            recommendations.extend([
                ('Длительность', f'{duration} сек - оптимально для Valorant'),
                ('Частота сбора', '120-300 Гц для быстрых реакций'),
                ('Фокус', 'Реакция и точность'),
                ('Совет', 'Практикуйте спреи и флик-шоты')
            ])
            
        # Заполняем таблицу
        self.recommendations_table.setRowCount(len(recommendations))
        
        for row, (param, value) in enumerate(recommendations):
            param_item = QTableWidgetItem(param)
            value_item = QTableWidgetItem(value)
            
            self.recommendations_table.setItem(row, 0, param_item)
            self.recommendations_table.setItem(row, 1, value_item)
            
        self.recommendations_table.resizeColumnsToContents()
        
        # Обновляем советы
        tips = self.get_game_tips(game)
        self.tips_text.setText(tips)
        
    def get_game_tips(self, game: str) -> str:
        """Получить советы для игры"""
        tips = {
            'CS2 (Counter-Strike 2)': '''
Советы для CS2:
• Используйте aim-тренировки для улучшения точности
• Практикуйте спреи на разных дистанциях
• Работайте над микро-корректировками
• Следите за экономикой и позиционированием
• Анализируйте свои ошибки после каждой сессии
''',
            'PUBG (PlayerUnknown\'s Battlegrounds)': '''
Советы для PUBG:
• Тренируйте прицеливание на разных дистанциях
• Работайте над управлением отдачей
• Практикуйте стрельбу на движущихся целях
• Следите за картой и позиционированием
• Анализируйте тактические решения
''',
            'Valorant': '''
Советы для Valorant:
• Практикуйте спреи и флик-шоты
• Работайте над управлением отдачей
• Используйте способности эффективно
• Анализируйте тимплеи
• Тренируйте реакцию на разных картах
'''
        }
        
        return tips.get(game, 'Советы недоступны для этой игры.')
        
    def start_analysis(self):
        """Начать анализ"""
        try:
            # Собираем настройки
            settings = {
                'game': self.game_combo.currentText(),
                'duration': self.duration_spin.value(),
                'analysis_type': self.analysis_group.checkedId(),
                'goal': self.goal_combo.currentText(),
                'collection_frequency': self.freq_spin.value(),
                'enable_filtering': self.filter_checkbox.isChecked(),
                'smoothing': self.smooth_spin.value(),
                'analysis_method': self.method_combo.currentText(),
                'analysis_accuracy': self.accuracy_group.checkedId(),
                'metrics': [key for key, checkbox in self.metrics_checkboxes.items() if checkbox.isChecked()]
            }
            
            # Валидация
            if not settings['game']:
                QMessageBox.warning(self, 'Ошибка', 'Пожалуйста, выберите игру')
                return
                
            if settings['duration'] < 30:
                QMessageBox.warning(self, 'Ошибка', 'Минимальная длительность сессии - 30 секунд')
                return
                
            # Подтверждение запуска
            confirm = QMessageBox.question(
                self, 'Подтверждение',
                f'Начать анализ для {settings["game"]}?\n'
                f'Длительность: {settings["duration"]} сек\n'
                f'Цель: {settings["goal"]}',
                QMessageBox.Yes | QMessageBox.No
            )
            
            if confirm == QMessageBox.Yes:
                self.game_selected.emit(settings['game'], settings)
                self.accept()
                
        except Exception as e:
            self.logger.error(f"Ошибка при запуске анализа: {e}")
            QMessageBox.critical(self, 'Ошибка', f'Не удалось начать анализ: {e}')

def create_game_selector(parent=None) -> GameSelectionDialog:
    """Создать диалог выбора игры"""
    return GameSelectionDialog(parent)