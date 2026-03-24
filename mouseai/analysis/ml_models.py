#!/usr/bin/env python3
"""
MLModels - Машинное обучение и нейросети для анализа мыши
"""

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.cluster import KMeans, DBSCAN
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
import pickle
import os
from pathlib import Path

@dataclass
class PlayerProfile:
    """Профиль игрока"""
    style: str  # 'flicker', 'tracker', 'micro_juster'
    skill_level: str  # 'beginner', 'intermediate', 'advanced', 'pro'
    accuracy: float
    consistency: float
    reaction_time: float
    movement_pattern: np.ndarray
    model_features: np.ndarray

class LSTMAnalyzer(nn.Module):
    """LSTM нейросеть для анализа последовательностей движений с оптимизацией"""
    
    def __init__(self, input_size=2, hidden_size=64, num_layers=2, output_size=4, dropout_rate=0.2):
        super(LSTMAnalyzer, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        # Оптимизированная архитектура
        self.lstm = nn.LSTM(
            input_size, 
            hidden_size, 
            num_layers, 
            batch_first=True,
            dropout=dropout_rate if num_layers > 1 else 0,
            bidirectional=False
        )
        
        # Batch normalization для стабилизации обучения
        self.batch_norm = nn.BatchNorm1d(hidden_size)
        self.dropout = nn.Dropout(dropout_rate)
        self.fc = nn.Linear(hidden_size, output_size)
        
        # Инициализация весов
        self._init_weights()
        
    def _init_weights(self):
        """Инициализация весов LSTM"""
        for name, param in self.lstm.named_parameters():
            if 'weight_ih' in name:
                nn.init.xavier_uniform_(param.data)
            elif 'weight_hh' in name:
                nn.init.orthogonal_(param.data)
            elif 'bias' in name:
                param.data.fill_(0)
                
    def forward(self, x):
        """Прямой проход с оптимизациями"""
        batch_size = x.size(0)
        
        # Инициализация скрытых состояний
        h0 = torch.zeros(self.num_layers, batch_size, self.hidden_size).to(x.device)
        c0 = torch.zeros(self.num_layers, batch_size, self.hidden_size).to(x.device)
        
        # LSTM проход
        lstm_out, _ = self.lstm(x, (h0, c0))
        
        # Берем последнее состояние
        last_output = lstm_out[:, -1, :]
        
        # Batch normalization
        if last_output.size(0) > 1:  # Только если batch_size > 1
            last_output = self.batch_norm(last_output)
            
        # Dropout и полносвязный слой
        output = self.dropout(last_output)
        output = self.fc(output)
        
        return output

class MLModels:
    """Класс для управления ML моделями"""
    
    def __init__(self):
        self.style_classifier = StyleClassifier()
        self.player_clustering = PlayerClustering()
        self.lstm_trainer = LSTMTrainer()
        
    def train_all(self, training_data: List[Tuple[List[Dict], str]]):
        """Обучить все модели"""
        print("🤖 Обучение ML моделей...")
        
        # Обучаем классификатор стилей
        self.style_classifier.train(training_data)
        
        # Обучаем кластеризацию
        mouse_data_list = [data for data, _ in training_data]
        self.player_clustering.fit(mouse_data_list)
        
        # Обучаем LSTM
        self.lstm_trainer.create_model()
        self.lstm_trainer.train_model(mouse_data_list, epochs=50)
        
        print("✅ Все ML модели обучены")
        
    def analyze_player(self, mouse_data: List[Dict]) -> Dict[str, Any]:
        """Провести полный анализ игрока"""
        results = {}
        
        # Классификация стиля
        style = self.style_classifier.predict(mouse_data)
        results['style'] = style
        
        # Кластеризация
        cluster = self.player_clustering.predict_cluster(mouse_data)
        cluster_description = self.player_clustering.get_cluster_description(cluster)
        results['cluster'] = cluster
        results['cluster_description'] = cluster_description
        
        # LSTM анализ
        pattern = self.lstm_trainer.predict_pattern(mouse_data)
        results['movement_pattern'] = pattern
        
        return results
        
    def save_models(self, directory: str):
        """Сохранить все модели"""
        Path(directory).mkdir(exist_ok=True)
        
        self.style_classifier.save_model(f"{directory}/style_classifier.pkl")
        self.player_clustering.save_model(f"{directory}/player_clustering.pkl")
        self.lstm_trainer.save_model(f"{directory}/lstm_model.pth")
        
        print(f"💾 ML модели сохранены в {directory}")
        
    def load_models(self, directory: str):
        """Загрузить все модели"""
        style_loaded = self.style_classifier.load_model(f"{directory}/style_classifier.pkl")
        clustering_loaded = self.player_clustering.load_model(f"{directory}/player_clustering.pkl")
        lstm_loaded = self.lstm_trainer.load_model(f"{directory}/lstm_model.pth")
        
        print(f"📂 ML модели загружены из {directory}")
        return style_loaded and clustering_loaded and lstm_loaded

class StyleClassifier:
    """Классификатор стилей игры"""
    
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
        self.classes_ = ['flicker', 'tracker', 'micro_juster', 'hybrid']
        
    def extract_features(self, mouse_data: List[Dict]) -> np.ndarray:
        """Извлечь признаки из данных мыши"""
        if not mouse_data:
            return np.zeros(10)
            
        positions = np.array([[d['x'], d['y']] for d in mouse_data if 'x' in d and 'y' in d])
        
        if len(positions) < 10:
            return np.zeros(10)
            
        # Рассчитываем признаки
        velocities = np.diff(positions, axis=0)
        speeds = np.linalg.norm(velocities, axis=1)
        
        features = [
            np.mean(speeds),           # Средняя скорость
            np.std(speeds),            # Стандартное отклонение скорости
            np.max(speeds),            # Максимальная скорость
            np.percentile(speeds, 25), # 25 перцентиль
            np.percentile(speeds, 75), # 75 перцентиль
            len(speeds[speeds > np.mean(speeds) * 2]),  # Количество быстрых движений
            np.mean(np.abs(np.diff(speeds))),            # Изменчивость скорости
            np.std(np.diff(speeds)),                     # Стандартное отклонение изменений скорости
            self._calculate_direction_changes(positions), # Изменения направления
            self._calculate_movement_efficiency(positions) # Эффективность движений
        ]
        
        return np.array(features)
        
    def _calculate_direction_changes(self, positions: np.ndarray) -> float:
        """Рассчитать изменения направления"""
        if len(positions) < 3:
            return 0.0
            
        directions = []
        for i in range(1, len(positions)):
            vec = positions[i] - positions[i-1]
            if np.linalg.norm(vec) > 0:
                angle = np.arctan2(vec[1], vec[0])
                directions.append(angle)
                
        if len(directions) < 2:
            return 0.0
            
        changes = np.abs(np.diff(directions))
        return np.mean(changes)
        
    def _calculate_movement_efficiency(self, positions: np.ndarray) -> float:
        """Рассчитать эффективность движений"""
        if len(positions) < 2:
            return 0.0
            
        start = positions[0]
        end = positions[-1]
        direct_distance = np.linalg.norm(end - start)
        
        path_distance = 0.0
        for i in range(1, len(positions)):
            path_distance += np.linalg.norm(positions[i] - positions[i-1])
            
        return direct_distance / path_distance if path_distance > 0 else 0.0
        
    def train(self, training_data: List[Tuple[List[Dict], str]]):
        """Обучить классификатор с оптимизацией"""
        if not training_data:
            print("❌ Нет данных для обучения StyleClassifier")
            return
            
        X = []
        y = []
        
        # Сбор данных с валидацией
        valid_samples = 0
        for mouse_data, style in training_data:
            features = self.extract_features(mouse_data)
            if not np.all(np.isfinite(features)):  # Проверка на NaN/inf
                continue
            X.append(features)
            y.append(style)
            valid_samples += 1
            
        if valid_samples < 10:
            print(f"❌ Недостаточно валидных данных для обучения: {valid_samples}")
            return
            
        X = np.array(X)
        y = np.array(y)
        
        # Проверка баланса классов
        unique_classes, class_counts = np.unique(y, return_counts=True)
        print(f"📊 Баланс классов: {dict(zip(unique_classes, class_counts))}")
        
        # Нормализация с проверкой
        try:
            X_scaled = self.scaler.fit_transform(X)
        except Exception as e:
            print(f"❌ Ошибка нормализации: {e}")
            return
        
        # Обучение с валидацией
        try:
            self.model.fit(X_scaled, y)
            self.is_trained = True
            
            # Оценка качества
            train_score = self.model.score(X_scaled, y)
            print(f"✅ StyleClassifier обучен на {len(X)} примерах, точность: {train_score:.3f}")
            
        except Exception as e:
            print(f"❌ Ошибка обучения: {e}")
        
    def predict(self, mouse_data: List[Dict]) -> str:
        """Предсказать стиль игры"""
        if not self.is_trained:
            return "unknown"
            
        features = self.extract_features(mouse_data)
        features_scaled = self.scaler.transform([features])
        
        prediction = self.model.predict(features_scaled)[0]
        probability = self.model.predict_proba(features_scaled)[0]
        
        return prediction
        
    def save_model(self, filepath: str):
        """Сохранить модель"""
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'is_trained': self.is_trained,
            'classes_': self.classes_
        }
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
            
    def load_model(self, filepath: str):
        """Загрузить модель"""
        if not os.path.exists(filepath):
            return False
            
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)
            
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.is_trained = model_data['is_trained']
        self.classes_ = model_data['classes_']
        
        return True

class PlayerClustering:
    """Кластеризация игроков по стилю игры"""
    
    def __init__(self, n_clusters=5):
        self.n_clusters = n_clusters
        self.kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        self.dbscan = DBSCAN(eps=0.5, min_samples=5)
        self.scaler = StandardScaler()
        self.is_fitted = False
        self.cluster_centers_ = None
        self.labels_ = None
        
    def extract_player_features(self, mouse_data: List[Dict]) -> np.ndarray:
        """Извлечь признаки игрока для кластеризации"""
        if not mouse_data:
            return np.zeros(15)
            
        positions = np.array([[d['x'], d['y']] for d in mouse_data if 'x' in d and 'y' in d])
        
        if len(positions) < 20:
            return np.zeros(15)
            
        # Рассчитываем комплексные признаки
        velocities = np.diff(positions, axis=0)
        speeds = np.linalg.norm(velocities, axis=1)
        
        accelerations = np.diff(speeds)
        
        features = [
            # Скоростные характеристики
            np.mean(speeds),
            np.std(speeds),
            np.max(speeds),
            np.median(speeds),
            
            # Ускорение
            np.mean(accelerations),
            np.std(accelerations),
            np.max(np.abs(accelerations)),
            
            # Точность и эффективность
            self._calculate_precision_score(positions),
            self._calculate_efficiency_score(positions),
            self._calculate_smoothness_score(speeds),
            
            # Паттерны движений
            self._calculate_pattern_complexity(positions),
            self._calculate_direction_variance(positions),
            self._calculate_micro_adjustments(speeds),
            
            # Временные характеристики
            len(speeds) / 100.0,  # Длительность
            np.std(np.diff(speeds))  # Стабильность
        ]
        
        return np.array(features)
        
    def _calculate_precision_score(self, positions: np.ndarray) -> float:
        """Рассчитать точность движений"""
        if len(positions) < 10:
            return 0.0
            
        # Рассчитываем отклонение от среднего направления
        start = positions[0]
        end = positions[-1]
        
        if np.allclose(start, end):
            return 0.0
            
        # Рассчитываем отклонения от прямой
        deviations = []
        for point in positions:
            numerator = abs((end[0]-start[0])*(start[1]-point[1]) - (start[0]-point[0])*(end[1]-start[1]))
            denominator = np.linalg.norm(end - start)
            if denominator > 0:
                deviations.append(numerator / denominator)
                
        return 1.0 / (1.0 + np.mean(deviations)) if deviations else 0.0
        
    def _calculate_efficiency_score(self, positions: np.ndarray) -> float:
        """Рассчитать эффективность движений"""
        if len(positions) < 2:
            return 0.0
            
        start = positions[0]
        end = positions[-1]
        direct_distance = np.linalg.norm(end - start)
        
        path_distance = 0.0
        for i in range(1, len(positions)):
            path_distance += np.linalg.norm(positions[i] - positions[i-1])
            
        return direct_distance / path_distance if path_distance > 0 else 0.0
        
    def _calculate_smoothness_score(self, speeds: np.ndarray) -> float:
        """Рассчитать плавность движений"""
        if len(speeds) < 5:
            return 0.0
            
        # Чем меньше изменение скорости, тем плавнее движение
        speed_changes = np.abs(np.diff(speeds))
        return 1.0 / (1.0 + np.mean(speed_changes))
        
    def _calculate_pattern_complexity(self, positions: np.ndarray) -> float:
        """Рассчитать сложность паттернов"""
        if len(positions) < 10:
            return 0.0
            
        # Используем Sample Entropy как меру сложности
        velocities = np.diff(positions, axis=0)
        speeds = np.linalg.norm(velocities, axis=1)
        
        # Упрощенный расчет сложности
        return np.std(speeds) / (np.mean(speeds) + 1e-6)
        
    def _calculate_direction_variance(self, positions: np.ndarray) -> float:
        """Рассчитать вариативность направлений"""
        if len(positions) < 3:
            return 0.0
            
        directions = []
        for i in range(1, len(positions)):
            vec = positions[i] - positions[i-1]
            if np.linalg.norm(vec) > 0:
                angle = np.arctan2(vec[1], vec[0])
                directions.append(angle)
                
        return np.var(directions) if directions else 0.0
        
    def _calculate_micro_adjustments(self, speeds: np.ndarray) -> float:
        """Рассчитать количество микро-корректировок"""
        if len(speeds) < 10:
            return 0.0
            
        # Микро-корректировки - это маленькие изменения скорости
        speed_changes = np.abs(np.diff(speeds))
        micro_adjustments = np.sum(speed_changes < np.mean(speeds) * 0.1)
        
        return micro_adjustments / len(speeds)
        
    def fit(self, player_data: List[List[Dict]]):
        """Обучить кластеризатор с оптимизацией"""
        if not player_data:
            print("❌ Нет данных для обучения PlayerClustering")
            return
            
        X = []
        valid_samples = 0
        
        # Сбор данных с валидацией
        for mouse_data in player_data:
            features = self.extract_player_features(mouse_data)
            if not np.all(np.isfinite(features)):  # Проверка на NaN/inf
                continue
            X.append(features)
            valid_samples += 1
            
        if valid_samples < self.n_clusters * 3:  # Минимум 3 точки на кластер
            print(f"❌ Недостаточно данных для кластеризации: {valid_samples}")
            return
            
        X = np.array(X)
        
        # Проверка на достаточное количество уникальных точек
        unique_points = len(np.unique(X, axis=0))
        if unique_points < self.n_clusters:
            print(f"❌ Недостаточно уникальных точек для {self.n_clusters} кластеров: {unique_points}")
            return
        
        # Нормализация с проверкой
        try:
            X_scaled = self.scaler.fit_transform(X)
        except Exception as e:
            print(f"❌ Ошибка нормализации: {e}")
            return
        
        # K-means кластеризация с валидацией
        try:
            self.kmeans.fit(X_scaled)
            self.labels_ = self.kmeans.labels_
            self.cluster_centers_ = self.kmeans.cluster_centers_
            self.is_fitted = True
            
            # DBSCAN для обнаружения выбросов
            self.dbscan.fit(X_scaled)
            
            # Оценка качества кластеризации
            if len(set(self.labels_)) > 1:
                score = silhouette_score(X_scaled, self.labels_)
                print(f"📊 Качество кластеризации: {score:.3f}")
                
            print(f"✅ PlayerClustering обучен на {len(X)} игроках, {self.n_clusters} кластеров")
            
        except Exception as e:
            print(f"❌ Ошибка кластеризации: {e}")
        
    def predict_cluster(self, mouse_data: List[Dict]) -> int:
        """Предсказать кластер игрока"""
        if not self.is_fitted:
            return -1
            
        features = self.extract_player_features(mouse_data)
        features_scaled = self.scaler.transform([features])
        
        cluster = self.kmeans.predict(features_scaled)[0]
        return cluster
        
    def get_cluster_description(self, cluster_id: int) -> str:
        """Получить описание кластера"""
        if not self.is_fitted or cluster_id >= self.n_clusters:
            return "Unknown cluster"
            
        center = self.cluster_centers_[cluster_id]
        
        # Интерпретация центроидов
        if center[0] > 0.7:  # Высокая средняя скорость
            if center[5] > 0.5:  # Высокое ускорение
                return "Агрессивный фликер"
            else:
                return "Плавный трекер"
        else:
            if center[9] > 0.5:  # Высокая эффективность
                return "Точный микроджастер"
            else:
                return "Нестабильный игрок"
                
    def save_model(self, filepath: str):
        """Сохранить модель кластеризации"""
        model_data = {
            'kmeans': self.kmeans,
            'dbscan': self.dbscan,
            'scaler': self.scaler,
            'is_fitted': self.is_fitted,
            'cluster_centers_': self.cluster_centers_,
            'labels_': self.labels_,
            'n_clusters': self.n_clusters
        }
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
            
    def load_model(self, filepath: str):
        """Загрузить модель кластеризации"""
        if not os.path.exists(filepath):
            return False
            
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)
            
        self.kmeans = model_data['kmeans']
        self.dbscan = model_data['dbscan']
        self.scaler = model_data['scaler']
        self.is_fitted = model_data['is_fitted']
        self.cluster_centers_ = model_data['cluster_centers_']
        self.labels_ = model_data['labels_']
        self.n_clusters = model_data['n_clusters']
        
        return True

class LSTMTrainer:
    """Тренер LSTM моделей"""
    
    def __init__(self):
        self.model = None
        self.optimizer = None
        self.criterion = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
    def create_model(self, input_size=2, hidden_size=64, num_layers=2, output_size=4):
        """Создать LSTM модель"""
        self.model = LSTMAnalyzer(input_size, hidden_size, num_layers, output_size)
        self.model.to(self.device)
        self.criterion = nn.CrossEntropyLoss()
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.001)
        
    def prepare_sequence_data(self, mouse_data: List[Dict], sequence_length=50) -> Tuple[torch.Tensor, torch.Tensor]:
        """Подготовить данные для LSTM"""
        positions = np.array([[d['x'], d['y']] for d in mouse_data if 'x' in d and 'y' in d])
        
        if len(positions) < sequence_length:
            return torch.tensor([]), torch.tensor([])
            
        # Нормализация
        positions_normalized = (positions - positions.mean(axis=0)) / (positions.std(axis=0) + 1e-8)
        
        sequences = []
        labels = []
        
        for i in range(len(positions_normalized) - sequence_length):
            seq = positions_normalized[i:i+sequence_length]
            label = self._classify_movement_pattern(seq)
            
            sequences.append(seq)
            labels.append(label)
            
        return torch.FloatTensor(sequences).to(self.device), torch.LongTensor(labels).to(self.device)
        
    def _classify_movement_pattern(self, sequence: np.ndarray) -> int:
        """Классифицировать паттерн движения"""
        # Простая классификация по характеристикам
        velocities = np.diff(sequence, axis=0)
        speeds = np.linalg.norm(velocities, axis=1)
        
        mean_speed = np.mean(speeds)
        max_speed = np.max(speeds)
        speed_variance = np.var(speeds)
        
        if max_speed > mean_speed * 3 and speed_variance > 0.1:
            return 0  # Флик
        elif mean_speed > 0.5 and speed_variance < 0.05:
            return 1  # Трекинг
        elif mean_speed < 0.3 and speed_variance > 0.1:
            return 2  # Микрокорректировки
        else:
            return 3  # Смешанный
        
    def train_model(self, training_data: List[List[Dict]], epochs=100):
        """Обучить LSTM модель с оптимизацией"""
        if self.model is None:
            self.create_model()
            
        if not training_data:
            print("❌ Нет данных для обучения LSTM")
            return
            
        self.model.train()
        
        # Подсчет валидных данных
        valid_sequences = 0
        for mouse_data in training_data:
            sequences, _ = self.prepare_sequence_data(mouse_data)
            valid_sequences += len(sequences)
            
        if valid_sequences == 0:
            print("❌ Нет валидных последовательностей для обучения")
            return
            
        print(f"📊 Найдено {valid_sequences} валидных последовательностей")
        
        # Обучение с прогрессом
        for epoch in range(epochs):
            total_loss = 0
            batch_count = 0
            valid_batches = 0
            
            for mouse_data in training_data:
                sequences, labels = self.prepare_sequence_data(mouse_data)
                
                if len(sequences) == 0:
                    continue
                    
                # Обучение на батче
                for i in range(0, len(sequences), 32):  # batch_size = 32
                    batch_sequences = sequences[i:i+32]
                    batch_labels = labels[i:i+32]
                    
                    if len(batch_sequences) == 0:
                        continue
                        
                    try:
                        self.optimizer.zero_grad()
                        outputs = self.model(batch_sequences)
                        loss = self.criterion(outputs, batch_labels)
                        loss.backward()
                        self.optimizer.step()
                        
                        total_loss += loss.item()
                        batch_count += 1
                        valid_batches += 1
                        
                    except Exception as e:
                        print(f"⚠️  Ошибка в батче: {e}")
                        continue
                    
            # Логирование прогресса
            if epoch % 10 == 0:
                avg_loss = total_loss / max(batch_count, 1)
                print(f"Epoch {epoch}/{epochs}, Average Loss: {avg_loss:.4f}, Valid Batches: {valid_batches}")
                
        print("✅ LSTM модель обучена")
        
    def predict_pattern(self, mouse_data: List[Dict]) -> str:
        """Предсказать паттерн движения с оптимизацией"""
        if self.model is None or not self.model.training:
            return "unknown"
            
        self.model.eval()
        
        sequences, _ = self.prepare_sequence_data(mouse_data)
        
        if len(sequences) == 0:
            return "unknown"
            
        try:
            with torch.no_grad():
                outputs = self.model(sequences[-1:])  # Последняя последовательность
                prediction = torch.argmax(outputs, dim=1).item()
                
            patterns = ['flick', 'tracking', 'micro_adjustments', 'mixed']
            return patterns[prediction]
            
        except Exception as e:
            print(f"⚠️  Ошибка предсказания LSTM: {e}")
            return "unknown"
        
    def save_model(self, filepath: str):
        """Сохранить LSTM модель"""
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
        }, filepath)
        
    def load_model(self, filepath: str):
        """Загрузить LSTM модель"""
        if not os.path.exists(filepath):
            return False
            
        checkpoint = torch.load(filepath, map_location=self.device)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        
        return True

def create_ml_models():
    """Фабрика для создания ML моделей"""
    return {
        'style_classifier': StyleClassifier(),
        'player_clustering': PlayerClustering(),
        'lstm_trainer': LSTMTrainer()
    }

# Пример использования
if __name__ == "__main__":
    print("🤖 Тестирование ML моделей...")
    
    # Создаем тестовые данные
    test_data = []
    for i in range(50):
        session = []
        for j in range(100):
            x = j * 5 + np.random.normal(0, 10)
            y = np.sin(j * 0.1) * 50 + np.random.normal(0, 5)
            session.append({'x': x, 'y': y})
        test_data.append(session)
        
    # Тест StyleClassifier
    print("\n🎯 Тест StyleClassifier:")
    classifier = StyleClassifier()
    
    # Создаем тренировочные данные
    training_data = []
    for session in test_data:
        # Случайно назначаем стили для теста
        style = np.random.choice(['flicker', 'tracker', 'micro_juster'])
        training_data.append((session, style))
        
    classifier.train(training_data)
    
    # Предсказание
    prediction = classifier.predict(test_data[0])
    print(f"   Предсказанный стиль: {prediction}")
    
    # Тест PlayerClustering
    print("\n📊 Тест PlayerClustering:")
    clustering = PlayerClustering(n_clusters=3)
    clustering.fit(test_data)
    
    cluster = clustering.predict_cluster(test_data[0])
    description = clustering.get_cluster_description(cluster)
    print(f"   Кластер: {cluster}, Описание: {description}")
    
    # Тест LSTM
    print("\n🧠 Тест LSTM:")
    lstm_trainer = LSTMTrainer()
    lstm_trainer.create_model()
    lstm_trainer.train_model(test_data[:10], epochs=10)
    
    pattern = lstm_trainer.predict_pattern(test_data[0])
    print(f"   Предсказанный паттерн: {pattern}")
    
    print("\n✅ Все ML модели протестированы!")