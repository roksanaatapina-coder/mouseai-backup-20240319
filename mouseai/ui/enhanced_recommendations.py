#!/usr/bin/env python3
"""
Enhanced Recommendations Panel Module
Интеллектуальная панель рекомендаций с AI анализом
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton,
    QScrollArea, QFrame, QSizePolicy, QGridLayout
)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont, QColor, QPalette, QTextCursor, QTextCharFormat
import json
import logging
from typing import Dict, Any, Optional


class EnhancedRecommendationsPanel(QWidget):
    """Интеллектуальная панель рекомендаций для MouseAI"""
    
    recommendations_updated = Signal(dict)
    
    def __init__(self, ai_client=None):
        super().__init__()
        self.ai_client = ai_client
        self.logger = logging.getLogger(__name__)
        self.current_analysis = None
        
        self.setup_ui()
        self.setup_styles()
    
    def setup_ui(self):
        """Настройка интерфейса панели рекомендаций"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Заголовок
        title_layout = QHBoxLayout()
        self.title_label = QLabel("🎯 AI Recommendations")
        self.title_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.title_label.setStyleSheet("color: #2196F3; margin-bottom: 5px;")
        title_layout.addWidget(self.title_label)
        
        # Статус
        self.status_label = QLabel("Status: Ready")
        self.status_label.setStyleSheet("color: #666; font-style: italic;")
        title_layout.addWidget(self.status_label)
        title_layout.addStretch()
        layout.addLayout(title_layout)
        
        # Основная область с рекомендациями
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
            QScrollArea { border: 1px solid #ddd; border-radius: 4px; }
            QScrollBar:vertical { width: 15px; }
            QScrollBar:horizontal { height: 15px; }
        """)
        
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setSpacing(15)
        self.content_layout.setContentsMargins(15, 15, 15, 15)
        
        # Блок анализа
        self.analysis_frame = self._create_analysis_frame()
        self.content_layout.addWidget(self.analysis_frame)
        
        # Блок рекомендаций
        self.recommendations_frame = self._create_recommendations_frame()
        self.content_layout.addWidget(self.recommendations_frame)
        
        # Блок упражнений
        self.exercises_frame = self._create_exercises_frame()
        self.content_layout.addWidget(self.exercises_frame)
        
        # Блок оборудования
        self.equipment_frame = self._create_equipment_frame()
        self.content_layout.addWidget(self.equipment_frame)
        
        # Блок расписания
        self.schedule_frame = self._create_schedule_frame()
        self.content_layout.addWidget(self.schedule_frame)
        
        # Блок прогресса
        self.progress_frame = self._create_progress_frame()
        self.content_layout.addWidget(self.progress_frame)
        
        self.scroll_area.setWidget(self.content_widget)
        layout.addWidget(self.scroll_area)
        
        # Кнопки управления
        buttons_layout = QHBoxLayout()
        
        self.refresh_btn = QPushButton("🔄 Refresh Recommendations")
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.refresh_btn.clicked.connect(self.refresh_recommendations)
        buttons_layout.addWidget(self.refresh_btn)
        
        self.export_btn = QPushButton("📄 Export to PDF")
        self.export_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        self.export_btn.clicked.connect(self.export_recommendations)
        buttons_layout.addWidget(self.export_btn)
        
        self.clear_btn = QPushButton("🗑️ Clear")
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        self.clear_btn.clicked.connect(self.clear_recommendations)
        buttons_layout.addWidget(self.clear_btn)
        
        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)
        
        # Изначально скрываем все блоки
        self._hide_all_frames()
    
    def setup_styles(self):
        """Настройка стилей для различных элементов"""
        self.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QFrame {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 15px;
            }
            QLabel {
                font-size: 12pt;
                color: #333;
            }
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px;
                background-color: #fafafa;
                font-size: 11pt;
            }
        """)
    
    def _create_analysis_frame(self):
        """Создание блока анализа"""
        frame = QFrame()
        layout = QVBoxLayout(frame)
        
        title = QLabel("📊 Performance Analysis")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        title.setStyleSheet("color: #1976D2; margin-bottom: 10px;")
        layout.addWidget(title)
        
        self.analysis_text = QTextEdit()
        self.analysis_text.setReadOnly(True)
        self.analysis_text.setMinimumHeight(120)
        self.analysis_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 10px;
                background-color: #f0f8ff;
                font-size: 11pt;
                line-height: 1.4;
            }
        """)
        layout.addWidget(self.analysis_text)
        
        return frame
    
    def _create_recommendations_frame(self):
        """Создание блока рекомендаций"""
        frame = QFrame()
        layout = QVBoxLayout(frame)
        
        title = QLabel("💡 Key Recommendations")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        title.setStyleSheet("color: #FF9800; margin-bottom: 10px;")
        layout.addWidget(title)
        
        self.recommendations_text = QTextEdit()
        self.recommendations_text.setReadOnly(True)
        self.recommendations_text.setMinimumHeight(100)
        self.recommendations_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 10px;
                background-color: #fff3e0;
                font-size: 11pt;
            }
        """)
        layout.addWidget(self.recommendations_text)
        
        return frame
    
    def _create_exercises_frame(self):
        """Создание блока упражнений"""
        frame = QFrame()
        layout = QVBoxLayout(frame)
        
        title = QLabel("🏋️ Training Exercises")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        title.setStyleSheet("color: #4CAF50; margin-bottom: 10px;")
        layout.addWidget(title)
        
        self.exercises_text = QTextEdit()
        self.exercises_text.setReadOnly(True)
        self.exercises_text.setMinimumHeight(100)
        self.exercises_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 10px;
                background-color: #e8f5e9;
                font-size: 11pt;
            }
        """)
        layout.addWidget(self.exercises_text)
        
        return frame
    
    def _create_equipment_frame(self):
        """Создание блока оборудования"""
        frame = QFrame()
        layout = QVBoxLayout(frame)
        
        title = QLabel("⚙️ Equipment Suggestions")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        title.setStyleSheet("color: #9C27B0; margin-bottom: 10px;")
        layout.addWidget(title)
        
        self.equipment_text = QTextEdit()
        self.equipment_text.setReadOnly(True)
        self.equipment_text.setMinimumHeight(80)
        self.equipment_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 10px;
                background-color: #f3e5f5;
                font-size: 11pt;
            }
        """)
        layout.addWidget(self.equipment_text)
        
        return frame
    
    def _create_schedule_frame(self):
        """Создание блока расписания"""
        frame = QFrame()
        layout = QVBoxLayout(frame)
        
        title = QLabel("📅 Practice Schedule")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        title.setStyleSheet("color: #00BCD4; margin-bottom: 10px;")
        layout.addWidget(title)
        
        self.schedule_text = QTextEdit()
        self.schedule_text.setReadOnly(True)
        self.schedule_text.setMinimumHeight(80)
        self.schedule_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 10px;
                background-color: #e0f7fa;
                font-size: 11pt;
            }
        """)
        layout.addWidget(self.schedule_text)
        
        return frame
    
    def _create_progress_frame(self):
        """Создание блока прогресса"""
        frame = QFrame()
        layout = QVBoxLayout(frame)
        
        title = QLabel("📈 Progress Tracking")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        title.setStyleSheet("color: #795548; margin-bottom: 10px;")
        layout.addWidget(title)
        
        self.progress_text = QTextEdit()
        self.progress_text.setReadOnly(True)
        self.progress_text.setMinimumHeight(80)
        self.progress_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 10px;
                background-color: #efebe9;
                font-size: 11pt;
            }
        """)
        layout.addWidget(self.progress_text)
        
        return frame
    
    def update_recommendations(self, session_data: Dict[str, Any]):
        """Обновление рекомендаций на основе AI анализа"""
        try:
            self.status_label.setText("Status: Analyzing...")
            self.status_label.setStyleSheet("color: #FF9800; font-style: italic;")
            
            if not self.ai_client:
                self._show_error("AI client not available")
                return
            
            # Выполнение AI анализа
            analysis = self.ai_client.analyze_session(session_data)
            self.current_analysis = analysis
            
            # Отображение результатов
            self._display_analysis(analysis)
            self._show_all_frames()
            
            self.status_label.setText("Status: Analysis complete")
            self.status_label.setStyleSheet("color: #4CAF50; font-style: italic; font-weight: bold;")
            
            # Сигнал об обновлении рекомендаций
            self.recommendations_updated.emit(analysis)
            
            self.logger.info("Recommendations updated successfully")
            
        except Exception as e:
            self.logger.error(f"Error updating recommendations: {e}")
            self._show_error(f"Error: {str(e)}")
    
    def _display_analysis(self, analysis: Dict[str, Any]):
        """Отображение результатов анализа"""
        # Анализ производительности
        analysis_text = analysis.get('analysis', 'No analysis available')
        self.analysis_text.setText(analysis_text)
        
        # Рекомендации
        recommendations = analysis.get('recommendations', [])
        recommendations_text = self._format_list(recommendations)
        self.recommendations_text.setText(recommendations_text)
        
        # Упражнения
        exercises = analysis.get('exercises', [])
        exercises_text = self._format_list(exercises)
        self.exercises_text.setText(exercises_text)
        
        # Оборудование
        equipment = analysis.get('equipment', 'No specific equipment recommendations')
        self.equipment_text.setText(equipment)
        
        # Расписание
        schedule = analysis.get('schedule', 'No specific schedule recommendations')
        self.schedule_text.setText(schedule)
        
        # Прогресс
        progress = analysis.get('progress_tracking', 'No progress tracking information')
        self.progress_text.setText(progress)
    
    def _format_list(self, items: list) -> str:
        """Форматирование списка в текст"""
        if not items:
            return "No items available"
        
        text = ""
        for i, item in enumerate(items, 1):
            text += f"{i}. {item}\n"
        
        return text.strip()
    
    def _show_error(self, error_message: str):
        """Отображение сообщения об ошибке"""
        self._hide_all_frames()
        self.analysis_text.setText(f"Error: {error_message}")
        self.analysis_frame.show()
        self.status_label.setText(f"Status: Error - {error_message}")
        self.status_label.setStyleSheet("color: #f44336; font-style: italic; font-weight: bold;")
    
    def _show_all_frames(self):
        """Показать все блоки"""
        self.analysis_frame.show()
        self.recommendations_frame.show()
        self.exercises_frame.show()
        self.equipment_frame.show()
        self.schedule_frame.show()
        self.progress_frame.show()
    
    def _hide_all_frames(self):
        """Скрыть все блоки"""
        self.analysis_frame.hide()
        self.recommendations_frame.hide()
        self.exercises_frame.hide()
        self.equipment_frame.hide()
        self.schedule_frame.hide()
        self.progress_frame.hide()
    
    def refresh_recommendations(self):
        """Обновление рекомендаций"""
        self.status_label.setText("Status: Refreshing...")
        self.status_label.setStyleSheet("color: #2196F3; font-style: italic;")
        
        # Имитация задержки для визуального эффекта
        QTimer.singleShot(1000, lambda: self._refresh_complete())
    
    def _refresh_complete(self):
        """Завершение обновления"""
        if self.current_analysis:
            self._display_analysis(self.current_analysis)
            self.status_label.setText("Status: Refreshed")
            self.status_label.setStyleSheet("color: #4CAF50; font-style: italic; font-weight: bold;")
        else:
            self.status_label.setText("Status: No data to refresh")
            self.status_label.setStyleSheet("color: #666; font-style: italic;")
    
    def export_recommendations(self):
        """Экспорт рекомендаций (заглушка для реализации)"""
        self.status_label.setText("Status: Export feature coming soon")
        self.status_label.setStyleSheet("color: #FF9800; font-style: italic;")
        # TODO: Реализовать экспорт в PDF/HTML
    
    def clear_recommendations(self):
        """Очистка рекомендаций"""
        self._hide_all_frames()
        self.current_analysis = None
        self.status_label.setText("Status: Cleared")
        self.status_label.setStyleSheet("color: #666; font-style: italic;")
    
    def get_current_analysis(self) -> Optional[Dict[str, Any]]:
        """Получение текущего анализа"""
        return self.current_analysis
    
    def set_ai_client(self, ai_client):
        """Установка AI клиента"""
        self.ai_client = ai_client
        self.logger.info("AI client updated in recommendations panel")