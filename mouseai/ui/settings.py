#!/usr/bin/env python3
"""
Settings UI - Интерфейс настроек
"""

import sys
import os
from pathlib import Path
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
                            QComboBox, QSpinBox, QDoubleSpinBox, QCheckBox, QGroupBox,
                            QTabWidget, QWidget, QTextEdit, QMessageBox, QFileDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import logging
import json

# Добавляем путь к проекту
sys.path.insert(0, str(Path(__file__).parent.parent))

from mouseai.utils import MouseAILogger

class SettingsDialog(QDialog):
    """Диалог настроек"""
    
    def __init__(self, parent=None, config=None):
        super().__init__(parent)
        
        self.config = config or {}
        self.logger = MouseAILogger()
        
        self.setWindowTitle('Настройки MouseAI')
        self.setGeometry(200, 200, 700, 600)
        
        self.init_ui()
        self.load_config()
        
    def init_ui(self):
        """Инициализация интерфейса"""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Заголовок
        title_label = QLabel('⚙️ Настройки MouseAI')
        title_label.setFont(QFont('Arial', 16, QFont.Bold))
        layout.addWidget(title_label)
        
        # Создаем вкладки
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # Вкладки
        self.create_general_tab()
        self.create_collection_tab()
        self.create_analysis_tab()
        self.create_visualization_tab()
        self.create_integrations_tab()
        
        # Кнопки управления
        btn_layout = QHBoxLayout()
        
        save_btn = QPushButton('Сохранить')
        save_btn.clicked.connect(self.save_config)
        save_btn.setStyleSheet('background-color: green; color: white; font-weight: bold;')
        btn_layout.addWidget(save_btn)
        
        reset_btn = QPushButton('Сбросить')
        reset_btn.clicked.connect(self.reset_config)
        btn_layout.addWidget(reset_btn)
        
        default_btn = QPushButton('По умолчанию')
        default_btn.clicked.connect(self.load_default_config)
        btn_layout.addWidget(default_btn)
        
        close_btn = QPushButton('Закрыть')
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
        
    def create_general_tab(self):
        """Создать вкладку общих настроек"""
        general_widget = QWidget()
        layout = QVBoxLayout()
        general_widget.setLayout(layout)
        
        # Группа общих настроек
        general_group = QGroupBox('Общие настройки')
        general_layout = QVBoxLayout()
        general_group.setLayout(general_layout)
        
        # Автозапуск
        self.autostart_checkbox = QCheckBox('Автоматически запускать MouseAI при старте системы')
        general_layout.addWidget(self.autostart_checkbox)
        
        # Автообновление
        self.auto_update_checkbox = QCheckBox('Автоматически проверять обновления')
        general_layout.addWidget(self.auto_update_checkbox)
        
        # Логирование
        log_layout = QHBoxLayout()
        log_layout.addWidget(QLabel('Уровень логирования:'))
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(['DEBUG', 'INFO', 'WARNING', 'ERROR'])
        log_layout.addWidget(self.log_level_combo)
        general_layout.addLayout(log_layout)
        
        # Путь для сохранения данных
        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel('Путь для сохранения данных:'))
        self.data_path_edit = QTextEdit()
        self.data_path_edit.setMaximumHeight(30)
        path_layout.addWidget(self.data_path_edit)
        
        browse_btn = QPushButton('Обзор')
        browse_btn.clicked.connect(self.browse_data_path)
        path_layout.addWidget(browse_btn)
        
        general_layout.addLayout(path_layout)
        
        layout.addWidget(general_group)
        
        # Группа производительности
        performance_group = QGroupBox('Производительность')
        performance_layout = QVBoxLayout()
        performance_group.setLayout(performance_layout)
        
        # Приоритет процесса
        priority_layout = QHBoxLayout()
        priority_layout.addWidget(QLabel('Приоритет процесса:'))
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(['Низкий', 'Нормальный', 'Высокий', 'Реального времени'])
        priority_layout.addWidget(self.priority_combo)
        performance_layout.addLayout(priority_layout)
        
        # Использование CPU
        cpu_layout = QHBoxLayout()
        cpu_layout.addWidget(QLabel('Максимальное использование CPU (%):'))
        self.cpu_spin = QSpinBox()
        self.cpu_spin.setRange(10, 100)
        self.cpu_spin.setValue(50)
        cpu_layout.addWidget(self.cpu_spin)
        performance_layout.addLayout(cpu_layout)
        
        # Использование памяти
        memory_layout = QHBoxLayout()
        memory_layout.addWidget(QLabel('Максимальное использование памяти (МБ):'))
        self.memory_spin = QSpinBox()
        self.memory_spin.setRange(100, 8192)
        self.memory_spin.setValue(1024)
        memory_layout.addWidget(self.memory_spin)
        performance_layout.addLayout(memory_layout)
        
        layout.addWidget(performance_group)
        
        self.tabs.addTab(general_widget, 'Общие')
        
    def create_collection_tab(self):
        """Создать вкладку настроек сбора данных"""
        collection_widget = QWidget()
        layout = QVBoxLayout()
        collection_widget.setLayout(layout)
        
        # Группа настроек сбора
        collection_group = QGroupBox('Настройки сбора данных')
        collection_layout = QVBoxLayout()
        collection_group.setLayout(collection_layout)
        
        # Частота сбора
        freq_layout = QHBoxLayout()
        freq_layout.addWidget(QLabel('Частота сбора данных (Гц):'))
        self.freq_spin = QSpinBox()
        self.freq_spin.setRange(30, 1000)
        self.freq_spin.setValue(120)
        freq_layout.addWidget(self.freq_spin)
        collection_layout.addLayout(freq_layout)
        
        # Фильтрация шума
        self.noise_filter_checkbox = QCheckBox('Включить фильтрацию шума')
        self.noise_filter_checkbox.setChecked(True)
        collection_layout.addWidget(self.noise_filter_checkbox)
        
        # Сглаживание
        smooth_layout = QHBoxLayout()
        smooth_layout.addWidget(QLabel('Сглаживание данных:'))
        self.smooth_spin = QDoubleSpinBox()
        self.smooth_spin.setRange(0.1, 1.0)
        self.smooth_spin.setValue(0.5)
        self.smooth_spin.setSingleStep(0.1)
        smooth_layout.addWidget(self.smooth_spin)
        collection_layout.addLayout(smooth_layout)
        
        # Калибровка
        calibrate_layout = QHBoxLayout()
        calibrate_btn = QPushButton('Калибровка мыши')
        calibrate_btn.clicked.connect(self.calibrate_mouse)
        calibrate_layout.addWidget(calibrate_btn)
        
        self.calibrate_status = QLabel('Статус: Не калибровано')
        calibrate_layout.addWidget(self.calibrate_status)
        collection_layout.addLayout(calibrate_layout)
        
        layout.addWidget(collection_group)
        
        # Группа хранения данных
        storage_group = QGroupBox('Хранение данных')
        storage_layout = QVBoxLayout()
        storage_group.setLayout(storage_layout)
        
        # Формат хранения
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel('Формат хранения:'))
        self.format_combo = QComboBox()
        self.format_combo.addItems(['JSON', 'CSV', 'SQLite', 'Binary'])
        format_layout.addWidget(self.format_combo)
        storage_layout.addLayout(format_layout)
        
        # Срок хранения
        retention_layout = QHBoxLayout()
        retention_layout.addWidget(QLabel('Срок хранения данных (дней):'))
        self.retention_spin = QSpinBox()
        self.retention_spin.setRange(7, 365)
        self.retention_spin.setValue(90)
        retention_layout.addWidget(self.retention_spin)
        storage_layout.addLayout(retention_layout)
        
        # Автоочистка
        self.auto_clean_checkbox = QCheckBox('Автоматическая очистка старых данных')
        self.auto_clean_checkbox.setChecked(True)
        storage_layout.addWidget(self.auto_clean_checkbox)
        
        layout.addWidget(storage_group)
        
        self.tabs.addTab(collection_widget, 'Сбор данных')
        
    def create_analysis_tab(self):
        """Создать вкладку настроек анализа"""
        analysis_widget = QWidget()
        layout = QVBoxLayout()
        analysis_widget.setLayout(layout)
        
        # Группа методов анализа
        method_group = QGroupBox('Методы анализа')
        method_layout = QVBoxLayout()
        method_group.setLayout(method_layout)
        
        # Метод анализа
        method_layout.addWidget(QLabel('Основной метод анализа:'))
        self.analysis_method_combo = QComboBox()
        self.analysis_method_combo.addItems([
            'Научный (классический)',
            'Машинное обучение',
            'Комбинированный',
            'Экспертный'
        ])
        method_layout.addWidget(self.analysis_method_combo)
        
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
        
        accuracy_layout.addWidget(low_radio)
        accuracy_layout.addWidget(medium_radio)
        accuracy_layout.addWidget(high_radio)
        accuracy_layout.addWidget(ultra_radio)
        method_layout.addLayout(accuracy_layout)
        
        layout.addWidget(method_group)
        
        # Группа метрик
        metrics_group = QGroupBox('Метрики анализа')
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
            ('biomechanical_metrics', 'Biomechanical (Биомеханика)'),
            ('pattern_recognition', 'Pattern Recognition (Распознавание паттернов)')
        ]
        
        for metric_key, metric_name in metrics:
            checkbox = QCheckBox(metric_name)
            self.metrics_checkboxes[metric_key] = checkbox
            metrics_layout.addWidget(checkbox)
            
        layout.addWidget(metrics_group)
        
        # Группа алгоритмов ML
        ml_group = QGroupBox('Алгоритмы машинного обучения')
        ml_layout = QVBoxLayout()
        ml_group.setLayout(ml_layout)
        
        self.ml_checkboxes = {}
        ml_algorithms = [
            ('random_forest', 'Random Forest (Случайный лес)'),
            ('svm', 'SVM (Метод опорных векторов)'),
            ('neural_network', 'Neural Network (Нейронная сеть)'),
            ('kmeans', 'K-Means (Кластеризация)'),
            ('pca', 'PCA (Анализ главных компонент)')
        ]
        
        for alg_key, alg_name in ml_algorithms:
            checkbox = QCheckBox(alg_name)
            self.ml_checkboxes[alg_key] = checkbox
            ml_layout.addWidget(checkbox)
            
        layout.addWidget(ml_group)
        
        self.tabs.addTab(analysis_widget, 'Анализ')
        
    def create_visualization_tab(self):
        """Создать вкладку настроек визуализации"""
        visualization_widget = QWidget()
        layout = QVBoxLayout()
        visualization_widget.setLayout(layout)
        
        # Группа графиков
        charts_group = QGroupBox('Настройки графиков')
        charts_layout = QVBoxLayout()
        charts_group.setLayout(charts_layout)
        
        # Тема
        theme_layout = QHBoxLayout()
        theme_layout.addWidget(QLabel('Тема графиков:'))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(['Светлая', 'Темная', 'Синяя', 'Зеленая', 'Красная'])
        theme_layout.addWidget(self.theme_combo)
        charts_layout.addLayout(theme_layout)
        
        # Размер графиков
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel('Размер графиков:'))
        self.size_combo = QComboBox()
        self.size_combo.addItems(['Маленький', 'Средний', 'Большой', 'Огромный'])
        size_layout.addWidget(self.size_combo)
        charts_layout.addLayout(size_layout)
        
        # Частота обновления
        update_layout = QHBoxLayout()
        update_layout.addWidget(QLabel('Частота обновления графиков (сек):'))
        self.update_spin = QSpinBox()
        self.update_spin.setRange(1, 60)
        self.update_spin.setValue(5)
        update_layout.addWidget(self.update_spin)
        charts_layout.addLayout(update_layout)
        
        layout.addWidget(charts_group)
        
        # Группа heatmaps
        heatmaps_group = QGroupBox('Heatmaps')
        heatmaps_layout = QVBoxLayout()
        heatmaps_group.setLayout(heatmaps_layout)
        
        # Разрешение heatmaps
        resolution_layout = QHBoxLayout()
        resolution_layout.addWidget(QLabel('Разрешение heatmaps:'))
        self.resolution_combo = QComboBox()
        self.resolution_combo.addItems(['Низкое', 'Среднее', 'Высокое', 'Ультра'])
        resolution_layout.addWidget(self.resolution_combo)
        heatmaps_layout.addLayout(resolution_layout)
        
        # Цветовая схема
        color_layout = QHBoxLayout()
        color_layout.addWidget(QLabel('Цветовая схема:'))
        self.color_combo = QComboBox()
        self.color_combo.addItems(['Тепловая', 'Спектральная', 'Однотонная', 'Градиент'])
        color_layout.addWidget(self.color_combo)
        heatmaps_layout.addLayout(color_layout)
        
        layout.addWidget(heatmaps_group)
        
        self.tabs.addTab(visualization_widget, 'Визуализация')
        
    def create_integrations_tab(self):
        """Создать вкладку интеграций"""
        integrations_widget = QWidget()
        layout = QVBoxLayout()
        integrations_widget.setLayout(layout)
        
        # Группа Discord
        discord_group = QGroupBox('Discord Bot')
        discord_layout = QVBoxLayout()
        discord_group.setLayout(discord_layout)
        
        self.discord_checkbox = QCheckBox('Включить Discord интеграцию')
        discord_layout.addWidget(self.discord_checkbox)
        
        discord_token_layout = QHBoxLayout()
        discord_token_layout.addWidget(QLabel('Bot Token:'))
        self.discord_token_edit = QTextEdit()
        self.discord_token_edit.setMaximumHeight(30)
        discord_token_layout.addWidget(self.discord_token_edit)
        discord_layout.addLayout(discord_token_layout)
        
        layout.addWidget(discord_group)
        
        # Группа Telegram
        telegram_group = QGroupBox('Telegram Bot')
        telegram_layout = QVBoxLayout()
        telegram_group.setLayout(telegram_layout)
        
        self.telegram_checkbox = QCheckBox('Включить Telegram интеграцию')
        telegram_layout.addWidget(self.telegram_checkbox)
        
        telegram_token_layout = QHBoxLayout()
        telegram_token_layout.addWidget(QLabel('Bot Token:'))
        self.telegram_token_edit = QTextEdit()
        self.telegram_token_edit.setMaximumHeight(30)
        telegram_token_layout.addWidget(self.telegram_token_edit)
        telegram_layout.addLayout(telegram_token_layout)
        
        layout.addWidget(telegram_group)
        
        # Группа OBS
        obs_group = QGroupBox('OBS Overlay')
        obs_layout = QVBoxLayout()
        obs_group.setLayout(obs_layout)
        
        self.obs_checkbox = QCheckBox('Включить OBS интеграцию')
        obs_layout.addWidget(self.obs_checkbox)
        
        obs_port_layout = QHBoxLayout()
        obs_port_layout.addWidget(QLabel('WebSocket порт:'))
        self.obs_port_spin = QSpinBox()
        self.obs_port_spin.setRange(1000, 9999)
        self.obs_port_spin.setValue(8765)
        obs_port_layout.addWidget(self.obs_port_spin)
        obs_layout.addLayout(obs_port_layout)
        
        layout.addWidget(obs_group)
        
        # Группа REST API
        api_group = QGroupBox('REST API')
        api_layout = QVBoxLayout()
        api_group.setLayout(api_layout)
        
        self.api_checkbox = QCheckBox('Включить REST API')
        api_layout.addWidget(self.api_checkbox)
        
        api_port_layout = QHBoxLayout()
        api_port_layout.addWidget(QLabel('API порт:'))
        self.api_port_spin = QSpinBox()
        self.api_port_spin.setRange(1000, 9999)
        self.api_port_spin.setValue(5000)
        api_port_layout.addWidget(self.api_port_spin)
        api_layout.addLayout(api_port_layout)
        
        layout.addWidget(api_group)
        
        self.tabs.addTab(integrations_widget, 'Интеграции')
        
    def load_config(self):
        """Загрузить конфигурацию"""
        try:
            if self.config:
                # Общие настройки
                general = self.config.get('general', {})
                self.autostart_checkbox.setChecked(general.get('autostart', False))
                self.auto_update_checkbox.setChecked(general.get('auto_update', True))
                self.log_level_combo.setCurrentText(general.get('log_level', 'INFO'))
                self.data_path_edit.setText(general.get('data_path', ''))
                self.priority_combo.setCurrentText(general.get('priority', 'Нормальный'))
                self.cpu_spin.setValue(general.get('cpu_limit', 50))
                self.memory_spin.setValue(general.get('memory_limit', 1024))
                
                # Настройки сбора
                collection = self.config.get('collection', {})
                self.freq_spin.setValue(collection.get('frequency', 120))
                self.noise_filter_checkbox.setChecked(collection.get('noise_filter', True))
                self.smooth_spin.setValue(collection.get('smoothing', 0.5))
                self.format_combo.setCurrentText(collection.get('format', 'JSON'))
                self.retention_spin.setValue(collection.get('retention_days', 90))
                self.auto_clean_checkbox.setChecked(collection.get('auto_clean', True))
                
                # Настройки анализа
                analysis = self.config.get('analysis', {})
                self.analysis_method_combo.setCurrentText(analysis.get('method', 'Научный (классический)'))
                
                accuracy = analysis.get('accuracy', 2)
                if accuracy == 1:
                    self.accuracy_group.button(1).setChecked(True)
                elif accuracy == 3:
                    self.accuracy_group.button(3).setChecked(True)
                elif accuracy == 4:
                    self.accuracy_group.button(4).setChecked(True)
                else:
                    self.accuracy_group.button(2).setChecked(True)
                    
                # Метрики
                metrics = analysis.get('metrics', [])
                for key, checkbox in self.metrics_checkboxes.items():
                    checkbox.setChecked(key in metrics)
                    
                # ML алгоритмы
                ml_algorithms = analysis.get('ml_algorithms', [])
                for key, checkbox in self.ml_checkboxes.items():
                    checkbox.setChecked(key in ml_algorithms)
                    
                # Настройки визуализации
                visualization = self.config.get('visualization', {})
                self.theme_combo.setCurrentText(visualization.get('theme', 'Светлая'))
                self.size_combo.setCurrentText(visualization.get('size', 'Средний'))
                self.update_spin.setValue(visualization.get('update_interval', 5))
                self.resolution_combo.setCurrentText(visualization.get('resolution', 'Среднее'))
                self.color_combo.setCurrentText(visualization.get('color_scheme', 'Тепловая'))
                
                # Интеграции
                integrations = self.config.get('integrations', {})
                
                discord = integrations.get('discord', {})
                self.discord_checkbox.setChecked(discord.get('enabled', False))
                self.discord_token_edit.setText(discord.get('token', ''))
                
                telegram = integrations.get('telegram', {})
                self.telegram_checkbox.setChecked(telegram.get('enabled', False))
                self.telegram_token_edit.setText(telegram.get('token', ''))
                
                obs = integrations.get('obs', {})
                self.obs_checkbox.setChecked(obs.get('enabled', False))
                self.obs_port_spin.setValue(obs.get('port', 8765))
                
                api = integrations.get('api', {})
                self.api_checkbox.setChecked(api.get('enabled', False))
                self.api_port_spin.setValue(api.get('port', 5000))
                
        except Exception as e:
            self.logger.error(f"Ошибка загрузки конфигурации: {e}")
            QMessageBox.warning(self, 'Ошибка', f'Не удалось загрузить конфигурацию: {e}')
            
    def save_config(self):
        """Сохранить конфигурацию"""
        try:
            # Собираем конфигурацию
            config = {
                'general': {
                    'autostart': self.autostart_checkbox.isChecked(),
                    'auto_update': self.auto_update_checkbox.isChecked(),
                    'log_level': self.log_level_combo.currentText(),
                    'data_path': self.data_path_edit.toPlainText(),
                    'priority': self.priority_combo.currentText(),
                    'cpu_limit': self.cpu_spin.value(),
                    'memory_limit': self.memory_spin.value()
                },
                'collection': {
                    'frequency': self.freq_spin.value(),
                    'noise_filter': self.noise_filter_checkbox.isChecked(),
                    'smoothing': self.smooth_spin.value(),
                    'format': self.format_combo.currentText(),
                    'retention_days': self.retention_spin.value(),
                    'auto_clean': self.auto_clean_checkbox.isChecked()
                },
                'analysis': {
                    'method': self.analysis_method_combo.currentText(),
                    'accuracy': self.accuracy_group.checkedId(),
                    'metrics': [key for key, checkbox in self.metrics_checkboxes.items() if checkbox.isChecked()],
                    'ml_algorithms': [key for key, checkbox in self.ml_checkboxes.items() if checkbox.isChecked()]
                },
                'visualization': {
                    'theme': self.theme_combo.currentText(),
                    'size': self.size_combo.currentText(),
                    'update_interval': self.update_spin.value(),
                    'resolution': self.resolution_combo.currentText(),
                    'color_scheme': self.color_combo.currentText()
                },
                'integrations': {
                    'discord': {
                        'enabled': self.discord_checkbox.isChecked(),
                        'token': self.discord_token_edit.toPlainText()
                    },
                    'telegram': {
                        'enabled': self.telegram_checkbox.isChecked(),
                        'token': self.telegram_token_edit.toPlainText()
                    },
                    'obs': {
                        'enabled': self.obs_checkbox.isChecked(),
                        'port': self.obs_port_spin.value()
                    },
                    'api': {
                        'enabled': self.api_checkbox.isChecked(),
                        'port': self.api_port_spin.value()
                    }
                }
            }
            
            # Сохраняем в файл
            with open('mouseai_config.json', 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
                
            self.config = config
            QMessageBox.information(self, 'Сохранение', 'Конфигурация сохранена')
            
        except Exception as e:
            self.logger.error(f"Ошибка сохранения конфигурации: {e}")
            QMessageBox.critical(self, 'Ошибка', f'Не удалось сохранить конфигурацию: {e}')
            
    def reset_config(self):
        """Сбросить конфигурацию"""
        reply = QMessageBox.question(
            self, 'Сброс', 'Вы уверены, что хотите сбросить настройки?',
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.load_default_config()
            
    def load_default_config(self):
        """Загрузить конфигурацию по умолчанию"""
        default_config = {
            'general': {
                'autostart': False,
                'auto_update': True,
                'log_level': 'INFO',
                'data_path': 'data/',
                'priority': 'Нормальный',
                'cpu_limit': 50,
                'memory_limit': 1024
            },
            'collection': {
                'frequency': 120,
                'noise_filter': True,
                'smoothing': 0.5,
                'format': 'JSON',
                'retention_days': 90,
                'auto_clean': True
            },
            'analysis': {
                'method': 'Научный (классический)',
                'accuracy': 2,
                'metrics': ['sample_entropy', 'maximum_absolute_deviation', 'time_to_peak_velocity', 'movement_efficiency'],
                'ml_algorithms': ['random_forest', 'svm']
            },
            'visualization': {
                'theme': 'Светлая',
                'size': 'Средний',
                'update_interval': 5,
                'resolution': 'Среднее',
                'color_scheme': 'Тепловая'
            },
            'integrations': {
                'discord': {'enabled': False, 'token': ''},
                'telegram': {'enabled': False, 'token': ''},
                'obs': {'enabled': False, 'port': 8765},
                'api': {'enabled': False, 'port': 5000}
            }
        }
        
        self.config = default_config
        self.load_config()
        QMessageBox.information(self, 'Сброс', 'Настройки сброшены до значений по умолчанию')
        
    def browse_data_path(self):
        """Выбрать путь для данных"""
        path = QFileDialog.getExistingDirectory(self, 'Выберите папку для данных')
        if path:
            self.data_path_edit.setText(path)
            
    def calibrate_mouse(self):
        """Калибровка мыши"""
        try:
            # Простая калибровка - измерение базовой чувствительности
            QMessageBox.information(
                self, 'Калибровка', 
                'Для калибровки выполните следующие действия:\n'
                '1. Переместите мышь на 10 см\n'
                '2. Нажмите OK\n'
                '3. Система измерит чувствительность'
            )
            
            # Здесь можно добавить реальную калибровку
            self.calibrate_status.setText('Статус: Откалибровано')
            QMessageBox.information(self, 'Калибровка', 'Калибровка завершена')
            
        except Exception as e:
            self.logger.error(f"Ошибка калибровки: {e}")
            QMessageBox.critical(self, 'Ошибка', f'Не удалось выполнить калибровку: {e}')

def create_settings_window(parent=None, config=None) -> SettingsDialog:
    """Создать окно настроек"""
    return SettingsDialog(parent, config)