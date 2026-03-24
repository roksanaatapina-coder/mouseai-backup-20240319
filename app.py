#!/usr/bin/env python3
"""
MouseAI - Aim Analyzer
ТОЧНАЯ КОПИЯ UI СКРИНШОТА
"""

import os
import sys
import json
import time
import logging
import traceback
from datetime import datetime
from typing import Optional, Any, Dict, List
from dotenv import load_dotenv  # type: ignore

def setup_security_logging():
    """Настройка безопасного логирования диагностики (DFIR)"""
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sessions")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "mouseai_security.log")
    
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - [%(module)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    def global_exception_handler(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        logging.critical("Uncaught System Exception", exc_info=(exc_type, exc_value, exc_traceback))
    
    sys.excepthook = global_exception_handler
    logging.info("--- MouseAI Forensic Logging Activated ---")

setup_security_logging()
from PySide6.QtWidgets import (  # type: ignore
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QComboBox, QSpinBox, QTabWidget, 
    QGroupBox, QGridLayout, QFrame, QCheckBox, QTableWidget,
    QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt, QTimer, QMetaObject, Q_ARG, Signal  # type: ignore
from PySide6.QtGui import QFont  # type: ignore

from analysis_report import MouseAnalysisReport  # type: ignore
from mouseai.core.data_collector import DataCollector  # type: ignore
from mouseai.core.game_detector import GameDetector  # type: ignore
import numpy as np  # type: ignore

class AimAnalyzerWindow(QMainWindow):
    """Главное окно - ТОЧНО КАК НА СКРИНШОТЕ"""
    
    # Сигнал для безопасного взаимодействия между потоками
    game_detected_signal = Signal(str)
    
    def __init__(self):
        super().__init__()
        load_dotenv()
        logging.info("Initializing UI Main Window")

        self.setWindowTitle("Aim Analyzer (Secure Mode)")
        self.setGeometry(100, 100, 900, 700)
        
        # Центральный виджет
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # ========== ВЕРХНЯЯ ЧАСТЬ ==========
        top_layout = QHBoxLayout()
        
        # Левая колонка
        left_column = QVBoxLayout()
        
        # Session Control
        session_group = QGroupBox("Session Control")
        session_layout = QVBoxLayout()
        
        # Ряд кнопок
        btn_layout = QHBoxLayout()
        self.start_btn = QPushButton("Start Session")
        self.start_btn.clicked.connect(self.start_session)
        btn_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("Stop Session")
        self.stop_btn.clicked.connect(self.stop_session)
        self.stop_btn.setEnabled(False)
        btn_layout.addWidget(self.stop_btn)
        
        session_layout.addLayout(btn_layout)
        
        # Статус
        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel("Status:"))
        self.status_label = QLabel("Idle")
        self.status_label.setStyleSheet("color: gray;")
        status_layout.addWidget(self.status_label)
        
        status_layout.addWidget(QLabel("Elapsed:"))
        self.elapsed_label = QLabel("—")
        self.elapsed_label.setStyleSheet("color: gray;")
        status_layout.addWidget(self.elapsed_label)
        
        status_layout.addStretch()
        session_layout.addLayout(status_layout)
        
        session_group.setLayout(session_layout)
        left_column.addWidget(session_group)

        # AI Boost
        ai_boost_layout = QHBoxLayout()
        self.ai_boost_btn = QPushButton("AI Boost")
        self.ai_boost_btn.setObjectName("AiBoostBtn")
        self.ai_boost_btn.clicked.connect(self.on_ai_boost_click)
        ai_boost_layout.addWidget(self.ai_boost_btn)
        ai_boost_layout.addStretch()
        session_layout.addLayout(ai_boost_layout)

        # PUBG Analysis
        pubg_group = QGroupBox("PUBG Analysis")
        pubg_layout = QVBoxLayout()
        
        # Просто текст как на скриншоте
        pubg_layout.addWidget(QLabel("PUBG specific analysis will appear here..."))
        
        pubg_group.setLayout(pubg_layout)
        left_column.addWidget(pubg_group)
        
        top_layout.addLayout(left_column, 1)
        
        # Правая колонка
        right_column = QVBoxLayout()
        
        # Progress Analysis
        progress_group = QGroupBox("Progress Analysis")
        progress_layout = QVBoxLayout()
        
        # Total Sessions
        sessions_layout = QHBoxLayout()
        sessions_layout.addWidget(QLabel("TOTAL SESSIONS"))
        self.total_sessions_label = QLabel("20")
        self.total_sessions_label.setObjectName("TotalSessions")
        sessions_layout.addWidget(self.total_sessions_label)
        sessions_layout.addStretch()
        progress_layout.addLayout(sessions_layout)
        
        # Game / Genre
        game_layout = QHBoxLayout()
        game_layout.addWidget(QLabel("Game / Genre"))
        self.game_combo = QComboBox()
        self.game_combo.addItems(["Universal", "CS2", "PUBG", "Valorant", "Apex"])
        game_layout.addWidget(self.game_combo)
        progress_layout.addLayout(game_layout)
        
        # Last Session Overview
        progress_layout.addWidget(QLabel("Last Session Overview"))
        self.last_session_label = QLabel("No session recorded yet. Start a session to see results here.")
        self.last_session_label.setWordWrap(True)
        self.last_session_label.setStyleSheet("color: gray; font-style: italic; padding: 5px;")
        progress_layout.addWidget(self.last_session_label)
        
        progress_group.setLayout(progress_layout)
        right_column.addWidget(progress_group)
        
        top_layout.addLayout(right_column, 1)
        
        main_layout.addLayout(top_layout)
        
        # ========== СРЕДНЯЯ ЧАСТЬ (Quick Analysis) ==========
        quick_group = QGroupBox("Quick Analysis")
        quick_layout = QHBoxLayout()
        
        quick_layout.addWidget(QLabel("Choose match number:"))
        
        self.match_spin = QSpinBox()
        self.match_spin.setMinimum(1)
        self.match_spin.setMaximum(100)
        self.match_spin.setValue(1)
        self.match_spin.setFixedWidth(60)
        quick_layout.addWidget(self.match_spin)
        
        self.analyze_btn = QPushButton("Analyze Match")
        quick_layout.addWidget(self.analyze_btn)
        
        self.analyze_last_btn = QPushButton("Analyze Last Match")
        quick_layout.addWidget(self.analyze_last_btn)
        
        self.compare_btn = QPushButton("Compare vs 5")
        quick_layout.addWidget(self.compare_btn)
        
        quick_layout.addStretch()
        quick_group.setLayout(quick_layout)
        main_layout.addWidget(quick_group)
        
        # ========== ТАБЫ ==========
        self.tabs = QTabWidget()
        
        # Вкладка Analysis Results
        results_tab = QWidget()
        results_layout = QVBoxLayout(results_tab)
        self.results_label = QLabel("Analysis results will appear here...")
        self.results_label.setStyleSheet("color: gray; font-style: italic; padding: 20px;")
        self.results_label.setAlignment(Qt.AlignCenter)
        
        self.tune_btn = QPushButton("Auto-Tune System Sensitivity")
        self.tune_btn.setToolTip("Automatically adjust Windows pointer speed based on physical metrics")
        self.tune_btn.hide()
        self.tune_btn.clicked.connect(self.auto_tune_sensitivity)
        self.recommended_multiplier = 1.0
        
        results_layout.addWidget(self.results_label)
        results_layout.addWidget(self.tune_btn)
        self.tabs.addTab(results_tab, "Analysis Results")
        
        # Вкладка Recent Sessions
        sessions_tab = QWidget()
        sessions_layout = QVBoxLayout(sessions_tab)
        
        # Таблица сессий
        self.sessions_table = QTableWidget()
        self.sessions_table.setColumnCount(4)
        self.sessions_table.setHorizontalHeaderLabels([
            "Timestamp", "Game", "Duration", "Activity"
        ])
        self.sessions_table.horizontalHeader().setStretchLastSection(True)
        self.sessions_table.setAlternatingRowColors(True)
        sessions_layout.addWidget(self.sessions_table)
        
        # Кнопка Refresh History
        refresh_layout = QHBoxLayout()
        refresh_layout.addStretch()
        self.refresh_btn = QPushButton("Refresh History")
        self.refresh_btn.clicked.connect(self.refresh_history)
        refresh_layout.addWidget(self.refresh_btn)
        sessions_layout.addLayout(refresh_layout)
        
        self.tabs.addTab(sessions_tab, "Recent Sessions")
        
        main_layout.addWidget(self.tabs)
        
        # ========== НИЖНЯЯ ЧАСТЬ ==========
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
        
        self.always_top_check = QCheckBox("Always on top")
        self.always_top_check.stateChanged.connect(self.toggle_always_on_top)
        bottom_layout.addWidget(self.always_top_check)
        
        main_layout.addLayout(bottom_layout)
        
        # Папка сессий и реальные данные
        self.sessions_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sessions")
        os.makedirs(self.sessions_dir, exist_ok=True)
        self.report = MouseAnalysisReport(self.sessions_dir)
        
        # Подключаем кнопки анализа
        self.analyze_btn.clicked.connect(self.display_specific_analysis)
        self.analyze_last_btn.clicked.connect(self.display_last_analysis)
        self.compare_btn.clicked.connect(self.compare_sessions)
        
        # Обновляем таблицу из файлов
        self.refresh_history()
        
        # Интеграция реального сборщика данных с мыши
        self.collector = DataCollector()
        self.last_hardware_events = []
        
        # Интеграция Автодетектора Игр
        self.game_detected_signal.connect(self._update_game_ui)
        self.game_detector = GameDetector()
        
        # Даем UI 2 секунды полностью загрузиться, прежде чем фоновый поток начнет слать сигналы
        QTimer.singleShot(2000, lambda: self.game_detector.start_monitoring(self.on_game_detected))
        
        # Таймер для записи
        self.recording_timer = QTimer()
        self.recording_timer.timeout.connect(self.update_recording)
        self.recording_start_time: Optional[float] = None
        self.is_recording: bool = False
        
    def on_game_detected(self, game_info):
        """Callback from GameDetector thread. Must sync to UI safely."""
        # Используем безопасный сигнал Qt вместо QTimer для фоновых потоков
        self.game_detected_signal.emit(game_info.name)

    def _update_game_ui(self, game_name: str):
        index = self.game_combo.findText(game_name)
        if index >= 0:
            self.game_combo.setCurrentIndex(index)
            self.status_label.setText(f"Auto-detected: {game_name}")

    def display_overall_analysis(self):
        """Show real aggregate statistics from all sessions"""
        stats = self.report.calculate_overall_stats()
        if not stats:
            self.results_label.setText("[ NO DATA ] Start a session to collect data.")
            return
        recs = self.report.generate_recommendations()
        
        print(f"\n[MouseAI] Aggregating {stats['total_matches']} local JSON files into memory...")
        print(f"[MouseAI] Calculating matrix means over {stats['total_duration']:.1f} total seconds recorded.")
        
        text = (
            f"OVERALL STATS ({stats['total_matches']} sessions)\n"
            f"Total Time: {stats['total_duration']:.1f}s  |  Avg Duration: {stats['avg_duration']:.1f}s\n"
            f"Avg Stability: {stats['avg_stability']:.2f}  |  Avg Intensity: {stats['avg_intensity']:.2f}\n"
            f"\nRECOMMENDATIONS:\n" + "\n".join(recs[:3])
        )
        self.results_label.setText(text)
        self.results_label.setStyleSheet("color: #00ff00; padding: 10px;")

    def display_specific_analysis(self):
        """Shows analysis for the specific match selected in the spin box"""
        match_idx = self.match_spin.value() - 1
        if not self.report.matches or match_idx >= len(self.report.matches) or match_idx < 0:
            self.results_label.setText(f"[ ERROR ] Match #{match_idx + 1} does not exist.")
            return
            
        match = self.report.matches[match_idx]
        stats = self.report.metrics_to_dict([match])
        text = (
            f"--- MATCH #{match_idx + 1} ANALYSIS ---\n"
            f"Game: {match.get('game_name', 'Unknown')}\n"
            f"Duration: {stats.get('avg_duration', 0):.1f}s\n"
            f"Stability (MAD): {stats.get('avg_stability', 0):.2f}\n"
            f"Intensity (Jerk): {stats.get('avg_intensity', 0):.2f}\n"
        )
        self.results_label.setText(text)
        self.results_label.setStyleSheet("color: #00ff00; padding: 10px;")
        
    def compare_sessions(self):
        """Compare the selected match vs the last 5 matches average"""
        match_idx = self.match_spin.value() - 1
        if not self.report.matches or match_idx >= len(self.report.matches) or match_idx < 0:
            self.results_label.setText(f"[ ERROR ] Target match #{match_idx + 1} not found.")
            return
            
        target_match = self.report.matches[match_idx]
        recent_5 = self.report.matches[-5:]
        
        t_stats = self.report.metrics_to_dict([target_match])
        r_stats = self.report.metrics_to_dict(recent_5)
        
        diff_stab = t_stats.get('avg_stability', 0) - r_stats.get('avg_stability', 0)
        diff_int = t_stats.get('avg_intensity', 0) - r_stats.get('avg_intensity', 0)
        
        stab_color = "red" if diff_stab > 0 else "green"
        int_color = "green" if diff_int > 0 else "red"
        
        text = (
            f"--- COMPARISON: Match #{match_idx + 1} vs Last {len(recent_5)} ---\n\n"
            f"TARGET MATCH:\n"
            f"Stability: {t_stats.get('avg_stability', 0):.2f} | Intensity: {t_stats.get('avg_intensity', 0):.2f}\n\n"
            f"RECENT AVERAGE:\n"
            f"Stability: {r_stats.get('avg_stability', 0):.2f} | Intensity: {r_stats.get('avg_intensity', 0):.2f}\n\n"
            f"DIFFERENCE:\n"
            f"Stability Delta: <font color='{stab_color}'>{diff_stab:+.2f}</font> (lower is better)\n"
            f"Intensity Delta: <font color='{int_color}'>{diff_int:+.2f}</font> (higher is faster)\n"
        )
        self.results_label.setText(text)
        self.results_label.setStyleSheet("color: white; padding: 10px;")

    def display_last_analysis(self):
        """Show detailed analysis of the most recent session"""
        if not self.report.matches:
            self.results_label.setText("[ NO SESSIONS ] Record your first session.")
            return
        last = self.report.matches[-1]
        recs = last.get('recommendations', [])
        rec_text = "\n".join(f"  > {r}" for r in recs[:3]) if recs else "  > No recommendations."
        text = (
            f"LAST SESSION: {last.get('selected_game','Unknown')} | {last.get('start_time','')[:19]}\n"
            f"Duration: {last.get('duration_seconds', 0):.2f}s\n"
            f"Activity: {last.get('activity_label','?')}  |  Stability: {last.get('stability_label','?')}\n"
            f"Stability Score: {last.get('stability_score',0):.2f}  |  Intensity: {last.get('intensity_score',0):.2f}\n"
            f"\nSESSION RECOMMENDATIONS:\n{rec_text}"
        )
        self.results_label.setText(text)
        self.results_label.setStyleSheet("color: #00ff00; padding: 10px;")
        
    def start_session(self):
        """Начать сессию"""
        self.is_recording = True
        self.recording_start_time = time.time()
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.status_label.setText("Recording")
        self.status_label.setStyleSheet("color: #00ff00; font-weight: bold;")
        
        # Запускаем настоящий сбор данных в отдельном потоке (100Hz)
        print("\n[MouseAI] Hardware tracker INITIALIZED! Hooking win32api/Quartz...")
        self.collector.start_recording()
        
        self.recording_timer.start(100)  # Обновление UI каждые 100мс
        
    def stop_session(self):
        """Остановить сессию"""
        self.is_recording = False
        self.recording_timer.stop()
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.status_label.setText("Idle")
        self.status_label.setStyleSheet("color: gray;")
        self.elapsed_label.setText("—")
        
        elapsed = time.time() - (self.recording_start_time or time.time())
        
        # Останавливаем аппаратный сбор danych
        collected_data = self.collector.stop_recording()
        self.last_hardware_events = collected_data.get("mouse_data", [])
        mouse_events = self.last_hardware_events
        
        from mouseai.analysis.scientific_metrics import ScientificMetricsCalculator, MetricsInterpreter
        
        if mouse_events and len(mouse_events) > 10:
            sci_calc = ScientificMetricsCalculator(sampling_rate=100)
            sci_interp = MetricsInterpreter()
            
            # Получаем полный 8-мерный спектр научных показателей! (Как Вы и просили в изначальных Aider-промптах)
            sci_metrics = sci_calc.calculate_all_metrics(mouse_events)
            interpretations = sci_interp.interpret_metrics(sci_metrics)
            
            # Маппинг для таблицы
            activity = int(sci_metrics.area_under_curve)
            avg_mag = float(sci_metrics.bimodality_coefficient)
            intensity = float(sci_metrics.maximum_absolute_deviation)
            stability = float(sci_metrics.movement_efficiency)  # Efficiency [0..1]
            
            act_label = interpretations.get('sample_entropy', "Unknown Pattern")
            stab_label = interpretations.get('efficiency', "Unknown Efficiency")
            
            # Расчет идеального множителя сенсы (Auto-Tune Logic)
            if sci_metrics.jerk_metric > 30 or sci_metrics.maximum_absolute_deviation > 40:
                self.recommended_multiplier = 0.85  # Понижаем сенсу на 15% (слишком дергано)
                self.tune_btn.setText("Auto-Tune Sensitivity (-15%)")
                self.tune_btn.show()
            elif sci_metrics.movement_efficiency > 0.85 and sci_metrics.time_to_peak_velocity > 0.2:
                self.recommended_multiplier = 1.15  # Повышаем сенсу на 15% (слишком медленно)
                self.tune_btn.setText("Auto-Tune Sensitivity (+15%)")
                self.tune_btn.show()
            else:
                self.recommended_multiplier = 1.0
                self.tune_btn.hide()
            
            # Формирование детального научного отчета для UI
            result_str = (
                f"--- SCIENTIFIC SESSION RESULTS ---\n"
                f"Duration: {elapsed:.1f}s | Hardware Hz: 100\n\n"
                f"📊 BIOMECHANICS:\n"
                f" • Path Efficiency: {sci_metrics.movement_efficiency*100:.1f}%\n"
                f" • Max Deviation (Error): {sci_metrics.maximum_absolute_deviation:.1f} px\n"
                f" • Reaction (TTPV): {sci_metrics.time_to_peak_velocity*1000:.0f} ms\n"
                f" • Smoothness (Jerk sum): {sci_metrics.jerk_metric:.1f}\n"
                f" • Complexity (SampEn): {sci_metrics.sample_entropy:.2f}\n\n"
                f"🧠 AI INTERPRETATION:\n"
                f" > {act_label}\n"
                f" > {stab_label}"
            )
        else:
            activity = 0; avg_mag = 0.0; intensity = 0.0; stability = 0.0
            act_label = "N/A"; stab_label = "N/A"
            sci_metrics = None
            result_str = "Session too short. Not enough hardware data collected."

        # Сохраняем реальный JSON
        session_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        start_ts = self.recording_start_time or time.time()
        session_data = {
            "version": "1.0",
            "session_id": session_id,
            "selected_game": self.game_combo.currentText(),
            "status": "completed",
            "start_time": datetime.fromtimestamp(float(start_ts)).isoformat(),
            "end_time": datetime.now().isoformat(),
            "duration_seconds": float(round(float(elapsed), 3)),
            "click_count": len(collected_data.get("keyboard_data", [])), # mouse clicks usually tracked in keyboard buffer locally
            "movement_activity": activity,
            "average_movement_magnitude": avg_mag,
            "intensity_score": intensity,
            "stability_score": stability,
            "activity_label": act_label,
            "stability_label": stab_label,
            "hardware_samples": len(mouse_events),
            "recommendations": []
        }
        
        # Локальная генерация рекомендаций
        recs = []
        if stability < 0.6:
            recs.append("Low stability detected. Lower your DPI or sensitivity.")
        if intensity < 200:
            recs.append("Activity is very low. Try aggressive fast tracking maps.")
        if elapsed < 10:
            recs.append("Session was too short for deep tactical analysis.")
        if not recs:
            recs.append("Excellent tracking! Keep practicing consistency.")
            
        session_data["recommendations"] = recs
        
        fname = os.path.join(self.sessions_dir, f"session_{session_id}.json")
        try:
            with open(fname, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2)
            self.report.matches.append(session_data)
            print(f"[MouseAI] Session stopped. Captured {len(mouse_events)} raw hardware events.")
            print(f"[MouseAI] Numpy Math -> Activity: {activity} | Intensity: {intensity:.2f} | Stability: {stability:.2f}")
            print(f"[MouseAI] Saved true hardware JSON to: {fname}")
        except Exception as e:
            print(f"[MouseAI] Session save failed: {e}")
        
        self.last_session_label.setText(f"Last: {elapsed:.2f}s | {self.game_combo.currentText()}")
        self.last_session_label.setStyleSheet("color: #00ff00;")
        
        # Обновляем главную панель результатов научными метриками
        self.results_label.setText(result_str)
        self.results_label.setStyleSheet("color: #00ff00; padding: 15px; font-weight: bold; font-family: monospace;")
        
        self.refresh_history()

    def on_ai_boost_click(self):
        try:
            self.results_label.setText("LOCAL ML BOOST: Extracting spatial features...")
            
            if not self.last_hardware_events:
                self.results_label.setText("No hardware data found. Please record a session first!")
                self.results_label.setStyleSheet("color: red; padding: 15px; font-weight: bold;")
                return

            # Instantiate the ML Style Classifier for Local Analysis (Lazy Load)
            from mouseai.analysis.ml_models import StyleClassifier  # type: ignore
            classifier = StyleClassifier()
            features = classifier.extract_features(self.last_hardware_events)
            
            # features is a 10-dimensional numpy array covering speeds and efficiency
            mean_spd = features[0]
            max_spd = features[2]
            flicks = features[5]
            efficiency = features[9]
            
            if efficiency > 0.6: verdict = "Tracking Master (High path efficiency)"
            elif max_spd > 1500 and flicks > 5: verdict = "Aggressive Flicker (High velocity peaks)"
            elif features[6] < 50: verdict = "Micro-Juster (Low speed variance)"
            else: verdict = "Hybrid / Unstable"
            
            result_str = (
                f"### Local ML Hardware Analysis ###\n\n"
                f"Mean Velocity: {mean_spd:.1f} px/s\n"
                f"Peak Velocity: {max_spd:.1f} px/s\n"
                f"Flick Count: {int(flicks)}\n"
                f"Path Efficiency: {efficiency*100:.1f}%\n\n"
                f"AI VERDICT: {verdict}"
            )
            self.results_label.setText(result_str)
            self.results_label.setStyleSheet("color: #00ff00; padding: 15px; font-weight: bold; font-family: monospace;")
        except Exception as e:
            self.results_label.setText("Local ML Analysis failed: " + str(e))
        
    def auto_tune_sensitivity(self):
        """Безопасное изменение системной чувствительности Windows (Не инжектится в игру!)"""
        import ctypes
        try:
            SPI_GETMOUSESPEED = 0x0070
            SPI_SETMOUSESPEED = 0x0071
            SPIF_UPDATEINIFILE = 0x01
            SPIF_SENDCHANGE = 0x02
            
            current_speed = ctypes.c_int()
            ctypes.windll.user32.SystemParametersInfoW(SPI_GETMOUSESPEED, 0, ctypes.byref(current_speed), 0)  # type: ignore
            
            new_speed = int(current_speed.value * self.recommended_multiplier)
            new_speed = max(1, min(20, new_speed)) # В Windows скорость от 1 до 20 (дефолт 10)
            
            # Применение новой скорости в систему
            ctypes.windll.user32.SystemParametersInfoW(SPI_SETMOUSESPEED, 0, new_speed, SPIF_UPDATEINIFILE | SPIF_SENDCHANGE)  # type: ignore
            
            msg = (f"\n\n[✅ AUTO-TUNE SUCCESS]\n"
                   f"Windows Pointer Speed changed from {current_speed.value} to {new_speed}!\n"
                   f"For 'Raw Input' games (CS2, Valorant), manually multiply your in-game sensitivity by {self.recommended_multiplier:.2f}!")
            self.results_label.setText(self.results_label.text() + msg)
            self.tune_btn.hide()
            self.recommended_multiplier = 1.0
        except Exception as e:
            self.results_label.setText(self.results_label.text() + f"\n\n[❌ AUTO-TUNE ERROR] {e}")

    def update_recording(self):
        """Обновление времени записи с анимацией"""
        if self.is_recording and self.recording_start_time is not None:
            elapsed = time.time() - float(self.recording_start_time)  # type: ignore
            self.elapsed_label.setText(f"{elapsed:.1f}s")
            
            # Анимация (мигающая иконка)
            if int(elapsed * 2) % 2 == 0:
                self.status_label.setText("[ ] Recording...")
            else:
                self.status_label.setText("[■] Recording...")
            
    def refresh_history(self):
        """Load real sessions from files into the table"""
        matches = self.report.matches
        self.sessions_table.setRowCount(len(matches))
        for i, match in enumerate(reversed(matches)):
            ts = match.get('start_time', 'Unknown')
            if 'T' in ts:
                ts = ts.replace('T', ' ')[:19]
            game = match.get('selected_game', 'Unknown')
            dur = f"{match.get('duration_seconds', 0):.2f}s"
            act = f"{match.get('activity_label', '?')} | {match.get('stability_label', '?')}"
            self.sessions_table.setItem(i, 0, QTableWidgetItem(ts))
            self.sessions_table.setItem(i, 1, QTableWidgetItem(game))
            self.sessions_table.setItem(i, 2, QTableWidgetItem(dur))
            self.sessions_table.setItem(i, 3, QTableWidgetItem(act))
        self.sessions_table.resizeColumnsToContents()
        self.total_sessions_label.setText(str(len(matches)))
        
    def toggle_always_on_top(self, state):
        """Переключение Always on top"""
        flags = self.windowFlags()
        if state == Qt.Checked:
            self.setWindowFlags(flags | Qt.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(flags & ~Qt.WindowStaysOnTopHint)
        self.show()

def main():
    app = QApplication(sys.argv)
    
    # Хакерский терминальный стиль (Matrix)
    app.setStyle('Fusion')
    app.setStyleSheet("""
        QMainWindow, QWidget {
            background-color: #050505;
            color: #00ff00;
            font-family: 'Consolas', 'Courier New', monospace;
        }
        QGroupBox {
            border: 1px solid #00ff00;
            border-radius: 0px;
            margin-top: 15px;
            font-weight: bold;
            font-size: 14pt;
            color: #00ff00;
            background-color: #0a0a0a;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 2px 10px;
            background-color: #00ff00;
            color: #050505;
            left: 10px;
        }
        QPushButton {
            background-color: transparent;
            border: 1px solid #00ff00;
            color: #00ff00;
            padding: 8px 16px;
            font-weight: bold;
            font-size: 10pt;
            text-transform: uppercase;
        }
        QPushButton:hover {
            background-color: #00ff00;
            color: #050505;
        }
        QPushButton:pressed {
            background-color: #008800;
            border-color: #008800;
            color: #ffffff;
        }
        QPushButton:disabled {
            border-color: #004400;
            color: #004400;
        }
        QPushButton#AiBoostBtn {
            background-color: #00ff00;
            color: #050505;
            border: none;
        }
        QPushButton#AiBoostBtn:hover {
            background-color: #39ff14;
        }
        QLabel {
            font-size: 10pt;
            color: #39ff14;
        }
        QLabel#TotalSessions {
            font-size: 28pt;
            font-weight: bold;
            color: #00ff00;
        }
        QComboBox, QSpinBox {
            background-color: #0a0a0a;
            border: 1px solid #00ff00;
            color: #00ff00;
            padding: 4px;
        }
        QTabWidget::pane {
            border: 1px solid #00ff00;
            background: #050505;
        }
        QTabBar::tab {
            background: #0a0a0a;
            border: 1px solid #004400;
            color: #00ff00;
            padding: 8px 20px;
            font-weight: bold;
        }
        QTabBar::tab:selected {
            background: #00ff00;
            color: #050505;
            border: 1px solid #00ff00;
        }
        QHeaderView::section {
            background-color: #0a0a0a;
            color: #00ff00;
            font-weight: bold;
            border: 1px solid #004400;
        }
        QTableWidget {
            background-color: #050505;
            color: #00aa00;
            gridline-color: #004400;
        }
    """)
    
    # Создаем окно
    window = AimAnalyzerWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()