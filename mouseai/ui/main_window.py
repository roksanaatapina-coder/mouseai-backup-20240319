#!/usr/bin/env python3
"""
MouseAI Main Window - Главное окно приложения
"""

import sys
import os
from pathlib import Path
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QLabel, QComboBox, QSpinBox, QGroupBox, QTextEdit,
                            QProgressBar, QStatusBar, QMenuBar, QMenu, QAction, QMessageBox,
                            QFileDialog, QTabWidget, QTableWidget, QTableWidgetItem,
                            QHeaderView, QCheckBox, QRadioButton, QButtonGroup)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QIcon
import logging
from datetime import datetime
import json

# Добавляем путь к проекту
sys.path.insert(0, str(Path(__file__).parent.parent))

# from mouseai.core import MouseAI
from mouseai.utils import MouseAILogger
from mouseai.visualization.dashboard import create_dashboard
from mouseai.core.mods_manager import ModsManager
from mouseai.ui.mods_window import ModsWindow

class MouseAIThread(QThread):
    """Поток для работы с MouseAI"""
    metrics_updated = pyqtSignal(dict)
    status_updated = pyqtSignal(dict)
    session_started = pyqtSignal()
    session_stopped = pyqtSignal()
    
    def __init__(self, mouseai_instance):
        super().__init__()
        self.mouseai = mouseai_instance
        self.running = False
        
    def run(self):
        """Запустить поток"""
        self.running = True
        
        while self.running:
            try:
                # Получаем текущий статус
                status = self.mouseai.get_status()
                self.status_updated.emit(status)
                
                # Получаем текущие метрики
                metrics = self.mouseai.get_current_metrics()
                if metrics:
                    self.metrics_updated.emit(metrics)
                    
                # Спим на 1 секунду
                self.sleep(1)
                
            except Exception as e:
                logging.error(f"Ошибка в потоке MouseAI: {e}")
                self.sleep(1)
                
    def stop(self):
        """Остановить поток"""
        self.running = False
        super().terminate()

class MouseAIMainWindow(QMainWindow):
    """Главное окно MouseAI"""
    
    def __init__(self):
        super().__init__()
        
        # Инициализация MouseAI
        # self.mouseai = MouseAI()
        self.logger = MouseAILogger()
        
        # Поток для MouseAI
        self.ai_thread = None
        
        # Инициализация менеджера режимов
        self.mods_manager = ModsManager()
        
        # Инициализация интерфейса
        self.init_ui()
        
        # Запуск потока
        self.start_ai_thread()
        
    def init_ui(self):
        """Инициализация пользовательского интерфейса"""
        self.setWindowTitle('MouseAI - Advanced Mouse Movement Analysis')
        self.setGeometry(100, 100, 1000, 700)
        
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Основной макет
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Создаем тулбар для быстрого доступа к режимам
        self.create_toolbar()
        main_layout.addWidget(self.toolbar)
        
        # Создаем вкладки
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # Вкладки
        self.create_main_tab()
        self.create_metrics_tab()
        self.create_sessions_tab()
        self.create_settings_tab()
        
        # Статус бар
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage('Готов к работе')
        
        # Меню
        self.create_menu()
        
        # Обновление каждую секунду
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_ui)
        self.timer.start(1000)
        
    def create_toolbar(self):
        """Создать тулбар для быстрого доступа к режимам"""
        self.toolbar = QWidget()
        toolbar_layout = QHBoxLayout()
        self.toolbar.setLayout(toolbar_layout)
        
        # Кнопка управления режимами
        self.mods_btn = QPushButton("🎮 РЕЖИМЫ")
        self.mods_btn.clicked.connect(self.open_mods_window)
        self.mods_btn.setStyleSheet("""
            QPushButton {
                background-color: #9C27B0;
                color: white;
                font-weight: bold;
                padding: 8px 15px;
                border-radius: 4px;
                font-size: 12pt;
            }
            QPushButton:hover {
                background-color: #7B1FA2;
            }
        """)
        toolbar_layout.addWidget(self.mods_btn)
        
        # Выпадающий список для быстрого переключения
        toolbar_layout.addWidget(QLabel("Режим:"))
        self.mod_combo = QComboBox()
        self.mod_combo.currentTextChanged.connect(self.on_mod_changed)
        toolbar_layout.addWidget(self.mod_combo)
        
        # Информация о текущем режиме
        self.mod_info_label = QLabel("CS2 PRO | DPI: 800 | Sens: 2.0")
        self.mod_info_label.setStyleSheet("color: #666; font-size: 10pt;")
        toolbar_layout.addWidget(self.mod_info_label)
        
        # Заполнитель для выравнивания
        toolbar_layout.addStretch()
        
        self.update_mod_combo()
        
    def create_menu(self):
        """Создать меню"""
        menubar = self.menuBar()
        
        # Файл
        file_menu = menubar.addMenu('Файл')
        
        exit_action = QAction('Выход', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Инструменты
        tools_menu = menubar.addMenu('Инструменты')
        
        dashboard_action = QAction('Панель управления', self)
        dashboard_action.triggered.connect(self.open_dashboard)
        tools_menu.addAction(dashboard_action)
        
        # Помощь
        help_menu = menubar.addMenu('Помощь')
        
        about_action = QAction('О программе', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def create_main_tab(self):
        """Создать главную вкладку"""
        main_widget = QWidget()
        layout = QVBoxLayout()
        main_widget.setLayout(layout)
        
        # Группа управления сессией
        session_group = QGroupBox('Управление сессией')
        session_layout = QHBoxLayout()
        session_group.setLayout(session_layout)
        
        # Выбор игры
        self.game_combo = QComboBox()
        self.game_combo.addItems(['CS2', 'PUBG', 'Valorant', 'Overwatch', 'Rainbow Six Siege'])
        session_layout.addWidget(QLabel('Игра:'))
        session_layout.addWidget(self.game_combo)
        
        # Длительность
        session_layout.addWidget(QLabel('Длительность (сек):'))
        self.duration_spin = QSpinBox()
        self.duration_spin.setRange(30, 3600)
        self.duration_spin.setValue(300)
        session_layout.addWidget(self.duration_spin)
        
        # Кнопки управления
        self.start_btn = QPushButton('Начать сессию')
        self.start_btn.clicked.connect(self.start_session)
        self.start_btn.setStyleSheet('background-color: green; color: white; font-weight: bold;')
        session_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton('Остановить сессию')
        self.stop_btn.clicked.connect(self.stop_session)
        self.stop_btn.setStyleSheet('background-color: red; color: white; font-weight: bold;')
        self.stop_btn.setEnabled(False)
        session_layout.addWidget(self.stop_btn)
        
        layout.addWidget(session_group)
        
        # Группа текущего статуса
        status_group = QGroupBox('Текущий статус')
        status_layout = QHBoxLayout()
        status_group.setLayout(status_layout)
        
        self.status_label = QLabel('Статус: Готов')
        self.status_label.setFont(QFont('Arial', 12, QFont.Bold))
        status_layout.addWidget(self.status_label)
        
        self.game_status_label = QLabel('Игра: Нет')
        self.game_status_label.setFont(QFont('Arial', 10))
        status_layout.addWidget(self.game_status_label)
        
        self.style_status_label = QLabel('Стиль: Не определен')
        self.style_status_label.setFont(QFont('Arial', 10))
        status_layout.addWidget(self.style_status_label)
        
        layout.addWidget(status_group)
        
        # Прогресс бар
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(QLabel('Прогресс сессии:'))
        layout.addWidget(self.progress_bar)
        
        self.tabs.addTab(main_widget, 'Главная')
        
    def create_metrics_tab(self):
        """Создать вкладку метрик"""
        metrics_widget = QWidget()
        layout = QVBoxLayout()
        metrics_widget.setLayout(layout)
        
        # Таблица метрик
        self.metrics_table = QTableWidget()
        self.metrics_table.setColumnCount(2)
        self.metrics_table.setHorizontalHeaderLabels(['Метрика', 'Значение'])
        self.metrics_table.horizontalHeader().setStretchLastSection(True)
        self.metrics_table.verticalHeader().setVisible(False)
        layout.addWidget(QLabel('Текущие метрики:'))
        layout.addWidget(self.metrics_table)
        
        # Текстовое поле для логов
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(QLabel('Логи:'))
        layout.addWidget(self.log_text)
        
        self.tabs.addTab(metrics_widget, 'Метрики')
        
    def create_sessions_tab(self):
        """Создать вкладку сессий"""
        sessions_widget = QWidget()
        layout = QVBoxLayout()
        sessions_widget.setLayout(layout)
        
        # Таблица сессий
        self.sessions_table = QTableWidget()
        self.sessions_table.setColumnCount(6)
        self.sessions_table.setHorizontalHeaderLabels(['Дата', 'Игра', 'Длительность', 'Стиль', 'Sample Entropy', 'Эффективность'])
        self.sessions_table.horizontalHeader().setStretchLastSection(True)
        self.sessions_table.verticalHeader().setVisible(False)
        layout.addWidget(QLabel('История сессий:'))
        layout.addWidget(self.sessions_table)
        
        # Кнопки управления
        btn_layout = QHBoxLayout()
        
        refresh_btn = QPushButton('Обновить')
        refresh_btn.clicked.connect(self.refresh_sessions)
        btn_layout.addWidget(refresh_btn)
        
        export_btn = QPushButton('Экспортировать')
        export_btn.clicked.connect(self.export_sessions)
        btn_layout.addWidget(export_btn)
        
        layout.addLayout(btn_layout)
        
        self.tabs.addTab(sessions_widget, 'Сессии')
        
    def create_settings_tab(self):
        """Создать вкладку настроек"""
        settings_widget = QWidget()
        layout = QVBoxLayout()
        settings_widget.setLayout(layout)
        
        # Группа настроек сбора данных
        data_group = QGroupBox('Настройки сбора данных')
        data_layout = QVBoxLayout()
        data_group.setLayout(data_layout)
        
        # Частота сбора
        freq_layout = QHBoxLayout()
        freq_layout.addWidget(QLabel('Частота сбора (Гц):'))
        self.freq_spin = QSpinBox()
        self.freq_spin.setRange(10, 1000)
        self.freq_spin.setValue(120)
        freq_layout.addWidget(self.freq_spin)
        data_layout.addLayout(freq_layout)
        
        # Фильтрация
        self.filter_checkbox = QCheckBox('Включить фильтрацию шума')
        self.filter_checkbox.setChecked(True)
        data_layout.addWidget(self.filter_checkbox)
        
        layout.addWidget(data_group)
        
        # Группа настроек анализа
        analysis_group = QGroupBox('Настройки анализа')
        analysis_layout = QVBoxLayout()
        analysis_group.setLayout(analysis_layout)
        
        # Метод анализа
        method_layout = QHBoxLayout()
        method_layout.addWidget(QLabel('Метод анализа:'))
        self.method_combo = QComboBox()
        self.method_combo.addItems(['Научный', 'Машинное обучение', 'Комбинированный'])
        method_layout.addWidget(self.method_combo)
        analysis_layout.addLayout(method_layout)
        
        # Точность анализа
        accuracy_layout = QHBoxLayout()
        accuracy_layout.addWidget(QLabel('Точность анализа:'))
        self.accuracy_group = QButtonGroup()
        
        low_radio = QRadioButton('Низкая')
        medium_radio = QRadioButton('Средняя')
        high_radio = QRadioButton('Высокая')
        
        self.accuracy_group.addButton(low_radio, 1)
        self.accuracy_group.addButton(medium_radio, 2)
        self.accuracy_group.addButton(high_radio, 3)
        
        medium_radio.setChecked(True)
        
        accuracy_layout.addWidget(low_radio)
        accuracy_layout.addWidget(medium_radio)
        accuracy_layout.addWidget(high_radio)
        analysis_layout.addLayout(accuracy_layout)
        
        layout.addWidget(analysis_group)
        
        # Кнопки сохранения
        save_layout = QHBoxLayout()
        
        save_btn = QPushButton('Сохранить настройки')
        save_btn.clicked.connect(self.save_settings)
        save_layout.addWidget(save_btn)
        
        reset_btn = QPushButton('Сбросить настройки')
        reset_btn.clicked.connect(self.reset_settings)
        save_layout.addWidget(reset_btn)
        
        layout.addLayout(save_layout)
        
        self.tabs.addTab(settings_widget, 'Настройки')
        
    def start_session(self):
        """Начать сессию"""
        game = self.game_combo.currentText()
        duration = self.duration_spin.value()
        
        try:
            self.mouseai.start_session(game, duration)
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.status_bar.showMessage(f'Сессия начата: {game}')
            self.logger.info(f"Начата сессия для игры: {game}, длительность: {duration} сек")
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Не удалось начать сессию: {e}')
            
    def stop_session(self):
        """Остановить сессию"""
        try:
            self.mouseai.stop_session()
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.status_bar.showMessage('Сессия остановлена')
            self.logger.info("Сессия остановлена")
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Не удалось остановить сессию: {e}')
            
    def update_ui(self):
        """Обновить интерфейс"""
        try:
            # Обновляем статус
            status = self.mouseai.get_status()
            
            # Обновляем метрики
            metrics = self.mouseai.get_current_metrics()
            if metrics:
                self.update_metrics_table(metrics)
                
            # Обновляем прогресс
            if status.get('session_duration', 0) > 0 and status.get('session_total_duration', 0) > 0:
                progress = (status['session_duration'] / status['session_total_duration']) * 100
                self.progress_bar.setValue(int(progress))
                
        except Exception as e:
            self.logger.error(f"Ошибка обновления UI: {e}")
            
    def update_metrics_table(self, metrics: dict):
        """Обновить таблицу метрик"""
        self.metrics_table.setRowCount(len(metrics))
        
        row = 0
        for key, value in metrics.items():
            metric_item = QTableWidgetItem(key.replace('_', ' ').title())
            value_item = QTableWidgetItem(f"{value:.4f}" if isinstance(value, float) else str(value))
            
            self.metrics_table.setItem(row, 0, metric_item)
            self.metrics_table.setItem(row, 1, value_item)
            row += 1
            
        self.metrics_table.resizeColumnsToContents()
        
    def refresh_sessions(self):
        """Обновить список сессий"""
        try:
            sessions = self.mouseai.get_session_history(20)
            
            self.sessions_table.setRowCount(len(sessions))
            
            for row, session in enumerate(sessions):
                date_item = QTableWidgetItem(session.get('timestamp', ''))
                game_item = QTableWidgetItem(session.get('game', ''))
                duration_item = QTableWidgetItem(f"{session.get('duration', 0)} сек")
                style_item = QTableWidgetItem(session.get('style', ''))
                
                metrics = session.get('metrics', {})
                entropy_item = QTableWidgetItem(f"{metrics.get('sample_entropy', 0):.4f}")
                efficiency_item = QTableWidgetItem(f"{metrics.get('movement_efficiency', 0):.4f}")
                
                self.sessions_table.setItem(row, 0, date_item)
                self.sessions_table.setItem(row, 1, game_item)
                self.sessions_table.setItem(row, 2, duration_item)
                self.sessions_table.setItem(row, 3, style_item)
                self.sessions_table.setItem(row, 4, entropy_item)
                self.sessions_table.setItem(row, 5, efficiency_item)
                
            self.sessions_table.resizeColumnsToContents()
            
        except Exception as e:
            self.logger.error(f"Ошибка обновления сессий: {e}")
            
    def export_sessions(self):
        """Экспортировать сессии"""
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self, 'Экспорт сессий', '', 'JSON Files (*.json);;CSV Files (*.csv)'
            )
            
            if filename:
                sessions = self.mouseai.get_session_history(100)
                
                if filename.endswith('.json'):
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(sessions, f, indent=2, ensure_ascii=False)
                elif filename.endswith('.csv'):
                    import csv
                    with open(filename, 'w', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        writer.writerow(['Дата', 'Игра', 'Длительность', 'Стиль', 'Sample Entropy', 'Эффективность'])
                        
                        for session in sessions:
                            metrics = session.get('metrics', {})
                            writer.writerow([
                                session.get('timestamp', ''),
                                session.get('game', ''),
                                session.get('duration', 0),
                                session.get('style', ''),
                                metrics.get('sample_entropy', 0),
                                metrics.get('movement_efficiency', 0)
                            ])
                            
                QMessageBox.information(self, 'Экспорт', f'Данные экспортированы в {filename}')
                
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Не удалось экспортировать данные: {e}')
            
    def save_settings(self):
        """Сохранить настройки"""
        try:
            settings = {
                'collection_frequency': self.freq_spin.value(),
                'enable_filtering': self.filter_checkbox.isChecked(),
                'analysis_method': self.method_combo.currentText(),
                'analysis_accuracy': self.accuracy_group.checkedId()
            }
            
            # Сохраняем в файл
            with open('mouseai_settings.json', 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
                
            # Применяем настройки
            self.mouseai.update_config(settings)
            
            QMessageBox.information(self, 'Настройки', 'Настройки сохранены')
            self.logger.info("Настройки сохранены")
            
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Не удалось сохранить настройки: {e}')
            
    def reset_settings(self):
        """Сбросить настройки"""
        try:
            # Сбрасываем значения по умолчанию
            self.freq_spin.setValue(120)
            self.filter_checkbox.setChecked(True)
            self.method_combo.setCurrentText('Научный')
            self.accuracy_group.button(2).setChecked(True)
            
            # Сохраняем
            self.save_settings()
            
            QMessageBox.information(self, 'Настройки', 'Настройки сброшены')
            
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Не удалось сбросить настройки: {e}')
            
    def start_ai_thread(self):
        """Запустить поток MouseAI"""
        if self.ai_thread:
            self.ai_thread.stop()
            
        # Создаем заглушку для mouseai если она не существует
        if not hasattr(self, 'mouseai'):
            class MockMouseAI:
                def get_status(self):
                    return {'current_game': 'Нет', 'current_style': 'Не определен', 'session_duration': 0, 'session_total_duration': 0}
                def get_current_metrics(self):
                    return {}
                def start_session(self, game, duration):
                    pass
                def stop_session(self):
                    pass
                def update_config(self, settings):
                    pass
                def get_session_history(self, count):
                    return []
            
            self.mouseai = MockMouseAI()
            
        self.ai_thread = MouseAIThread(self.mouseai)
        self.ai_thread.metrics_updated.connect(self.update_metrics_table)
        self.ai_thread.status_updated.connect(self.update_status)
        self.ai_thread.start()
        
    def update_status(self, status: dict):
        """Обновить статус"""
        current_game = status.get('current_game', 'Нет')
        current_style = status.get('current_style', 'Не определен')
        session_duration = status.get('session_duration', 0)
        
        self.status_label.setText(f'Статус: {current_game if current_game != "Нет" else "Готов"}')
        self.game_status_label.setText(f'Игра: {current_game}')
        self.style_status_label.setText(f'Стиль: {current_style}')
        
        # Обновляем цвет статуса
        if current_game != 'Нет':
            self.status_label.setStyleSheet('color: green')
        else:
            self.status_label.setStyleSheet('color: black')
            
    def open_dashboard(self):
        """Открыть панель управления"""
        try:
            dashboard = create_dashboard()
            
            # Добавляем текущие сессии в дашборд
            sessions = self.mouseai.get_session_history(50)
            for session in sessions:
                dashboard.add_session(session)
                
            # Генерируем отчет
            results = dashboard.generate_dashboard_report('dashboard_output')
            
            QMessageBox.information(
                self, 
                'Панель управления', 
                f'Отчеты сгенерированы:\n{chr(10).join(results.values())}'
            )
            
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Не удалось открыть панель управления: {e}')
            
    def show_about(self):
        """Показать информацию о программе"""
        about_text = """
        <h2>MouseAI</h2>
        <p>Advanced Mouse Movement Analysis</p>
        <p>Версия: 1.0.0</p>
        <p>Автор: MouseAI Team</p>
        <p>Описание: Продвинутый анализ движений мыши для улучшения игровых навыков</p>
        """
        
        QMessageBox.about(self, 'О программе', about_text)
        
    def update_mod_combo(self):
        """Обновить список режимов"""
        self.mod_combo.clear()
        for mod in self.mods_manager.get_all_mods():
            self.mod_combo.addItem(mod.name)
        
        if self.mods_manager.current_mod:
            index = self.mod_combo.findText(self.mods_manager.current_mod.name)
            if index >= 0:
                self.mod_combo.setCurrentIndex(index)
            self.update_mod_info()

    def on_mod_changed(self, mod_name):
        """Смена режима"""
        for mod in self.mods_manager.get_all_mods():
            if mod.name == mod_name:
                self.mods_manager.set_current_mod(mod.id)
                self.update_mod_info()
                self.statusBar().showMessage(f"Активирован режим: {mod.name}")
                break

    def update_mod_info(self):
        """Обновить информацию о текущем режиме"""
        if self.mods_manager.current_mod:
            mod = self.mods_manager.current_mod
            info_text = f"{mod.name} | DPI: {mod.dpi} | Sens: {mod.sensitivity} | {mod.game}"
            self.mod_info_label.setText(info_text)
            
            # Обновляем выбор игры в основном окне если виджет существует
            if hasattr(self, 'game_combo'):
                game_index = self.game_combo.findText(mod.game)
                if game_index >= 0:
                    self.game_combo.setCurrentIndex(game_index)

    def open_mods_window(self):
        """Открыть окно управления режимами"""
        window = ModsWindow(self.mods_manager, self)
        window.mod_changed.connect(self.on_mod_changed_from_window)
        window.exec_()

    def on_mod_changed_from_window(self, mod_id):
        """Обработка смены режима из окна"""
        mod = self.mods_manager.get_mod_by_id(mod_id)
        if mod:
            self.update_mod_combo()
            self.statusBar().showMessage(f"Активирован режим: {mod.name}")

    def closeEvent(self, event):
        """Обработка закрытия окна"""
        try:
            if self.ai_thread:
                self.ai_thread.stop()
                
            self.mouseai.stop_session()
            self.logger.info("MouseAI остановлен")
            
        except Exception as e:
            self.logger.error(f"Ошибка при закрытии: {e}")
            
        event.accept()

def main():
    """Главная функция"""
    app = QApplication(sys.argv)
    
    # Устанавливаем стиль
    app.setStyle('Fusion')
    
    window = MouseAIMainWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()