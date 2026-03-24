#!/usr/bin/env python3
"""
Окно управления режимами для MouseAI
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget, 
    QListWidgetItem, QPushButton, QLabel, QMessageBox,
    QFileDialog, QInputDialog, QFormLayout, QComboBox,
    QSpinBox, QDoubleSpinBox, QCheckBox, QGroupBox,
    QLineEdit
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
import os
from datetime import datetime

class ModsWindow(QDialog):
    """Окно управления режимами"""
    
    mod_changed = pyqtSignal(str)  # Сигнал при смене режима
    
    def __init__(self, mods_manager, parent=None):
        super().__init__(parent)
        self.mods_manager = mods_manager
        self.setWindowTitle("Управление режимами")
        self.setGeometry(200, 200, 600, 500)
        self.setup_ui()
        self.load_mods()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Список режимов
        self.mod_list = QListWidget()
        self.mod_list.itemClicked.connect(self.on_mod_selected)
        layout.addWidget(QLabel("📁 МОИ РЕЖИМЫ:"))
        layout.addWidget(self.mod_list)
        
        # Кнопки управления
        buttons_layout = QHBoxLayout()
        
        self.new_btn = QPushButton("➕ НОВЫЙ")
        self.new_btn.clicked.connect(self.create_mod)
        buttons_layout.addWidget(self.new_btn)
        
        self.edit_btn = QPushButton("✏️ РЕДАКТИРОВАТЬ")
        self.edit_btn.clicked.connect(self.edit_mod)
        buttons_layout.addWidget(self.edit_btn)
        
        self.delete_btn = QPushButton("🗑️ УДАЛИТЬ")
        self.delete_btn.clicked.connect(self.delete_mod)
        buttons_layout.addWidget(self.delete_btn)
        
        layout.addLayout(buttons_layout)
        
        # Кнопки экспорта/импорта
        share_layout = QHBoxLayout()
        
        self.export_btn = QPushButton("📤 ЭКСПОРТ")
        self.export_btn.clicked.connect(self.export_mod)
        share_layout.addWidget(self.export_btn)
        
        self.import_btn = QPushButton("📥 ИМПОРТ")
        self.import_btn.clicked.connect(self.import_mod)
        share_layout.addWidget(self.import_btn)
        
        self.share_btn = QPushButton("🔗 ПОДЕЛИТЬСЯ")
        self.share_btn.clicked.connect(self.share_mod)
        share_layout.addWidget(self.share_btn)
        
        layout.addLayout(share_layout)
        
        # Кнопка закрытия
        close_btn = QPushButton("ЗАКРЫТЬ")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
    
    def load_mods(self):
        """Загрузить режимы в список"""
        self.mod_list.clear()
        for mod in self.mods_manager.get_all_mods():
            item = QListWidgetItem(f"{'✓ ' if mod.id == (self.mods_manager.current_mod and self.mods_manager.current_mod.id) else '  '}{mod.name}")
            item.setData(Qt.UserRole, mod.id)
            item.setToolTip(f"Жанр: {mod.genre}\nИгра: {mod.game}\nDPI: {mod.dpi}\nЧувствительность: {mod.sensitivity}")
            
            # Выделяем текущий режим
            if self.mods_manager.current_mod and mod.id == self.mods_manager.current_mod.id:
                font = item.font()
                font.setBold(True)
                item.setFont(font)
            
            self.mod_list.addItem(item)
    
    def on_mod_selected(self, item):
        """Выбор режима"""
        mod_id = item.data(Qt.UserRole)
        if mod_id:
            self.mods_manager.set_current_mod(mod_id)
            self.mod_changed.emit(mod_id)
            self.load_mods()  # Обновить список
            QMessageBox.information(self, "Режим выбран", f"Активирован режим: {item.text()}")
    
    def create_mod(self):
        """Создать новый режим"""
        dialog = ModEditDialog(self.mods_manager, parent=self)
        if dialog.exec_():
            self.load_mods()
            QMessageBox.information(self, "Режим создан", "Новый режим успешно создан!")
    
    def edit_mod(self):
        """Редактировать режим"""
        current_item = self.mod_list.currentItem()
        if current_item:
            mod_id = current_item.data(Qt.UserRole)
            mod = self.mods_manager.get_mod_by_id(mod_id)
            if mod:
                dialog = ModEditDialog(self.mods_manager, mod, self)
                if dialog.exec_():
                    self.load_mods()
                    QMessageBox.information(self, "Режим обновлён", "Режим успешно обновлён!")
    
    def delete_mod(self):
        """Удалить режим"""
        current_item = self.mod_list.currentItem()
        if current_item:
            mod_id = current_item.data(Qt.UserRole)
            mod = self.mods_manager.get_mod_by_id(mod_id)
            if mod and mod.is_default:
                QMessageBox.warning(self, "Нельзя удалить", "Дефолтный режим нельзя удалить!")
                return
            
            reply = QMessageBox.question(self, "Подтверждение", 
                                        f"Удалить режим '{current_item.text()}'?",
                                        QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.mods_manager.delete_mod(mod_id)
                self.load_mods()
                QMessageBox.information(self, "Режим удалён", "Режим успешно удалён!")
    
    def export_mod(self):
        """Экспортировать режим"""
        current_item = self.mod_list.currentItem()
        if current_item:
            mod_id = current_item.data(Qt.UserRole)
            filepath, _ = QFileDialog.getSaveFileName(
                self, "Сохранить режим", 
                f"{current_item.text()}.json",
                "JSON Files (*.json)"
            )
            if filepath:
                if self.mods_manager.export_mod(mod_id, filepath):
                    QMessageBox.information(self, "Экспорт", f"Режим сохранён в:\n{filepath}")
    
    def import_mod(self):
        """Импортировать режим"""
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Импортировать режим", "",
            "JSON Files (*.json)"
        )
        if filepath:
            if self.mods_manager.import_mod(filepath):
                self.load_mods()
                QMessageBox.information(self, "Импорт", "Режим успешно импортирован!")
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось импортировать режим")
    
    def share_mod(self):
        """Поделиться режимом"""
        current_item = self.mod_list.currentItem()
        if current_item:
            mod_id = current_item.data(Qt.UserRole)
            mod = self.mods_manager.get_mod_by_id(mod_id)
            if mod:
                # Сохраняем во временный файл
                temp_file = os.path.join(os.path.expanduser("~"), "Desktop", f"{mod.name}.json")
                if self.mods_manager.export_mod(mod_id, temp_file):
                    QMessageBox.information(
                        self, 
                        "Режим готов к отправке", 
                        f"Файл режима сохранён на рабочем столе:\n{temp_file}\n\n"
                        f"Отправь этот файл другу. Он сможет импортировать его в свою программу."
                    )


class ModEditDialog(QDialog):
    """Диалог создания/редактирования режима"""
    
    def __init__(self, mods_manager, mod=None, parent=None):
        super().__init__(parent)
        self.mods_manager = mods_manager
        self.mod = mod
        self.setWindowTitle("Новый режим" if not mod else "Редактировать режим")
        self.setGeometry(300, 300, 500, 600)
        self.setup_ui()
        
        if mod:
            self.load_mod_data()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Основные настройки
        form_layout = QFormLayout()
        
        self.name_edit = QLineEdit()
        form_layout.addRow("Название:", self.name_edit)
        
        self.genre_combo = QComboBox()
        self.genre_combo.addItems(["Tactical FPS", "Battle Royale", "Hero Shooter", "RPG", "Universal"])
        form_layout.addRow("Жанр:", self.genre_combo)
        
        self.game_combo = QComboBox()
        self.game_combo.addItems(["CS2", "Valorant", "PUBG", "Apex Legends", "Overwatch 2", "Fortnite", "Custom"])
        self.game_combo.setEditable(True)
        form_layout.addRow("Игра:", self.game_combo)
        
        layout.addLayout(form_layout)
        
        # Настройки мыши
        mouse_group = QGroupBox("НАСТРОЙКИ МЫШИ")
        mouse_layout = QFormLayout()
        
        self.dpi_spin = QSpinBox()
        self.dpi_spin.setRange(100, 32000)
        self.dpi_spin.setValue(800)
        mouse_layout.addRow("DPI:", self.dpi_spin)
        
        self.sens_spin = QDoubleSpinBox()
        self.sens_spin.setRange(0.1, 10.0)
        self.sens_spin.setSingleStep(0.1)
        self.sens_spin.setValue(2.0)
        mouse_layout.addRow("Чувствительность:", self.sens_spin)
        
        self.polling_spin = QSpinBox()
        self.polling_spin.setRange(125, 8000)
        self.polling_spin.setValue(1000)
        mouse_layout.addRow("Частота опроса (Гц):", self.polling_spin)
        
        mouse_group.setLayout(mouse_layout)
        layout.addWidget(mouse_group)
        
        # ML модель
        ml_group = QGroupBox("ML МОДЕЛЬ")
        ml_layout = QFormLayout()
        
        self.ml_combo = QComboBox()
        self.ml_combo.addItems(["Random Forest", "SVM", "Neural Network", "LSTM", "K-Means"])
        ml_layout.addRow("Модель:", self.ml_combo)
        
        ml_group.setLayout(ml_layout)
        layout.addWidget(ml_group)
        
        # Особенности
        features_group = QGroupBox("ОСОБЕННОСТИ АНАЛИЗА")
        features_layout = QVBoxLayout()
        
        self.feature_flicks = QCheckBox("Анализ фликов")
        self.feature_tracking = QCheckBox("Анализ трекинга")
        self.feature_recoil = QCheckBox("Анализ отдачи")
        self.feature_micro = QCheckBox("Анализ микрокоррекций")
        self.feature_crosshair = QCheckBox("Анализ позиции прицела")
        
        features_layout.addWidget(self.feature_flicks)
        features_layout.addWidget(self.feature_tracking)
        features_layout.addWidget(self.feature_recoil)
        features_layout.addWidget(self.feature_micro)
        features_layout.addWidget(self.feature_crosshair)
        
        features_group.setLayout(features_layout)
        layout.addWidget(features_group)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        
        self.save_btn = QPushButton("💾 СОХРАНИТЬ")
        self.save_btn.clicked.connect(self.save_mod)
        buttons_layout.addWidget(self.save_btn)
        
        self.cancel_btn = QPushButton("❌ ОТМЕНА")
        self.cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
    
    def load_mod_data(self):
        """Загрузить данные режима для редактирования"""
        self.name_edit.setText(self.mod.name)
        self.genre_combo.setCurrentText(self.mod.genre)
        self.game_combo.setCurrentText(self.mod.game)
        self.dpi_spin.setValue(self.mod.dpi)
        self.sens_spin.setValue(self.mod.sensitivity)
        self.polling_spin.setValue(self.mod.polling_rate)
        self.ml_combo.setCurrentText(self.mod.ml_model)
        
        # Особенности
        self.feature_flicks.setChecked("flicks" in self.mod.features)
        self.feature_tracking.setChecked("tracking" in self.mod.features)
        self.feature_recoil.setChecked("recoil_control" in self.mod.features)
        self.feature_micro.setChecked("micro_adjustments" in self.mod.features)
        self.feature_crosshair.setChecked("crosshair_placement" in self.mod.features)
    
    def save_mod(self):
        """Сохранить режим"""
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Ошибка", "Введите название режима!")
            return
        
        features = []
        if self.feature_flicks.isChecked():
            features.append("flicks")
        if self.feature_tracking.isChecked():
            features.append("tracking")
        if self.feature_recoil.isChecked():
            features.append("recoil_control")
        if self.feature_micro.isChecked():
            features.append("micro_adjustments")
        if self.feature_crosshair.isChecked():
            features.append("crosshair_placement")
        
        if self.mod:
            # Обновляем существующий
            self.mods_manager.update_mod(
                self.mod.id,
                name=name,
                genre=self.genre_combo.currentText(),
                game=self.game_combo.currentText(),
                dpi=self.dpi_spin.value(),
                sensitivity=self.sens_spin.value(),
                polling_rate=self.polling_spin.value(),
                ml_model=self.ml_combo.currentText(),
                features=features
            )
        else:
            # Создаём новый
            from mouseai.core.mods_manager import GameMod
            new_mod = GameMod(
                id="",
                name=name,
                genre=self.genre_combo.currentText(),
                game=self.game_combo.currentText(),
                dpi=self.dpi_spin.value(),
                sensitivity=self.sens_spin.value(),
                polling_rate=self.polling_spin.value(),
                ml_model=self.ml_combo.currentText(),
                features=features,
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            )
            self.mods_manager.add_mod(new_mod)
        
        self.accept()