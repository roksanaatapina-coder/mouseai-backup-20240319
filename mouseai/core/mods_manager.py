#!/usr/bin/env python3
"""
Система управления режимами (Mods) для MouseAI
"""

import json
import os
from dataclasses import dataclass, asdict
from typing import List, Optional
from datetime import datetime
import shutil
from pathlib import Path

@dataclass
class GameMod:
    """Класс для хранения режима игры"""
    id: str
    name: str
    genre: str
    game: str
    dpi: int
    sensitivity: float
    polling_rate: int
    ml_model: str
    features: List[str]
    created_at: str
    updated_at: str
    is_default: bool = False
    
    def to_dict(self):
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data):
        return cls(**data)

class ModsManager:
    """Менеджер режимов"""
    
    def __init__(self, data_dir="mods"):
        self.data_dir = data_dir
        self.mods_file = os.path.join(data_dir, "mods.json")
        self.mods: List[GameMod] = []
        self.current_mod: Optional[GameMod] = None
        self._ensure_dir()
        self._load_mods()
    
    def _ensure_dir(self):
        """Создать папку для режимов"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def _load_mods(self):
        """Загрузить все режимы из файла"""
        if os.path.exists(self.mods_file):
            with open(self.mods_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.mods = [GameMod.from_dict(m) for m in data.get('mods', [])]
                current_id = data.get('current_mod_id')
                if current_id:
                    self.current_mod = self.get_mod_by_id(current_id)
        
        # Если нет режимов, создать дефолтные
        if not self.mods:
            self._create_default_mods()
    
    def _save_mods(self):
        """Сохранить все режимы"""
        data = {
            'mods': [m.to_dict() for m in self.mods],
            'current_mod_id': self.current_mod.id if self.current_mod else None,
            'updated_at': datetime.now().isoformat()
        }
        with open(self.mods_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _create_default_mods(self):
        """Создать дефолтные режимы"""
        default_mods = [
            GameMod(
                id="cs2_pro",
                name="CS2 PRO",
                genre="Tactical FPS",
                game="CS2",
                dpi=800,
                sensitivity=2.0,
                polling_rate=1000,
                ml_model="Random Forest",
                features=["flicks", "tracking", "micro_adjustments"],
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
                is_default=True
            ),
            GameMod(
                id="pubg_sniper",
                name="PUBG SNIPER",
                genre="Battle Royale",
                game="PUBG",
                dpi=400,
                sensitivity=3.0,
                polling_rate=1000,
                ml_model="Neural Network",
                features=["recoil_control", "tracking", "snap_shots"],
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
                is_default=False
            ),
            GameMod(
                id="valorant_pro",
                name="VALORANT PRO",
                genre="Tactical FPS",
                game="Valorant",
                dpi=800,
                sensitivity=1.5,
                polling_rate=1000,
                ml_model="SVM",
                features=["first_shot", "flicks", "crosshair_placement"],
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
                is_default=False
            ),
            GameMod(
                id="apex_tracker",
                name="APEX TRACKER",
                genre="Battle Royale",
                game="Apex Legends",
                dpi=1200,
                sensitivity=2.5,
                polling_rate=1000,
                ml_model="LSTM",
                features=["tracking", "movement", "flicks"],
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
                is_default=False
            )
        ]
        self.mods = default_mods
        self.current_mod = default_mods[0]
        self._save_mods()
    
    def get_all_mods(self) -> List[GameMod]:
        """Получить все режимы"""
        return self.mods
    
    def get_mod_by_id(self, mod_id: str) -> Optional[GameMod]:
        """Получить режим по ID"""
        for mod in self.mods:
            if mod.id == mod_id:
                return mod
        return None
    
    def add_mod(self, mod: GameMod):
        """Добавить новый режим"""
        mod.id = mod.name.lower().replace(' ', '_')
        mod.created_at = datetime.now().isoformat()
        mod.updated_at = datetime.now().isoformat()
        self.mods.append(mod)
        self._save_mods()
        return mod.id
    
    def update_mod(self, mod_id: str, **kwargs):
        """Обновить режим"""
        mod = self.get_mod_by_id(mod_id)
        if mod:
            for key, value in kwargs.items():
                if hasattr(mod, key):
                    setattr(mod, key, value)
            mod.updated_at = datetime.now().isoformat()
            self._save_mods()
            return True
        return False
    
    def delete_mod(self, mod_id: str):
        """Удалить режим"""
        mod = self.get_mod_by_id(mod_id)
        if mod and not mod.is_default:
            self.mods = [m for m in self.mods if m.id != mod_id]
            if self.current_mod and self.current_mod.id == mod_id:
                self.current_mod = self.mods[0] if self.mods else None
            self._save_mods()
            return True
        return False
    
    def set_current_mod(self, mod_id: str):
        """Установить текущий режим"""
        mod = self.get_mod_by_id(mod_id)
        if mod:
            self.current_mod = mod
            self._save_mods()
            return True
        return False
    
    def export_mod(self, mod_id: str, filepath: str):
        """Экспортировать режим в файл"""
        mod = self.get_mod_by_id(mod_id)
        if mod:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(mod.to_dict(), f, ensure_ascii=False, indent=2)
            return True
        return False
    
    def import_mod(self, filepath: str) -> bool:
        """Импортировать режим из файла"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Проверяем что это файл режима
            if 'name' in data and 'game' in data:
                mod = GameMod.from_dict(data)
                mod.id = mod.name.lower().replace(' ', '_')
                mod.created_at = datetime.now().isoformat()
                mod.updated_at = datetime.now().isoformat()
                
                # Проверяем нет ли такого уже
                if not self.get_mod_by_id(mod.id):
                    self.mods.append(mod)
                    self._save_mods()
                    return True
        except Exception as e:
            print(f"Ошибка импорта: {e}")
        return False