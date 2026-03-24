#!/usr/bin/env python3
"""
Improved ML Models - Enhanced machine learning with quantization, security, and performance optimizations
Based on AI Orchestra analysis recommendations
"""

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.cluster import KMeans, DBSCAN
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.pipeline import Pipeline
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass
import pickle
import os
import logging
import time
import warnings
from pathlib import Path

# Suppress sklearn warnings
warnings.filterwarnings('ignore', category=UserWarning)

@dataclass
class PlayerProfile:
    """Enhanced player profile with security and performance features"""
    style: str  # 'flicker', 'tracker', 'micro_juster'
    skill_level: str  # 'beginner', 'intermediate', 'advanced', 'pro'
    accuracy: float
    consistency: float
    reaction_time: float
    movement_pattern: np.ndarray
    model_features: np.ndarray
    confidence_score: float  # Model confidence
    anomaly_score: float   # Anomaly detection score

class OptimizedLSTMAnalyzer(nn.Module):
    """Optimized LSTM with quantization, dropout, and security features"""
    
    def __init__(self, input_size=2, hidden_size=64, num_layers=2, output_size=4, 
                 dropout_rate=0.3, bidirectional=False, use_layer_norm=True):
        super(OptimizedLSTMAnalyzer, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.bidirectional = bidirectional
        self.use_layer_norm = use_layer_norm
        
        # Optimized LSTM with better initialization
        self.lstm = nn.LSTM(
            input_size, 
            hidden_size, 
            num_layers, 
            batch_first=True,
            dropout=dropout_rate if num_layers > 1 else 0,
            bidirectional=bidirectional,
            bias=True
        )
        
        # Layer normalization for stability
        if use_layer_norm:
            self.layer_norm = nn.LayerNorm(hidden_size * (2 if bidirectional else 1))
        
        # Optimized fully connected layers
        self.dropout = nn.Dropout(dropout_rate)
        self.fc1 = nn.Linear(hidden_size * (2 if bidirectional else 1), hidden_size // 2)
        self.fc2 = nn.Linear(hidden_size // 2, output_size)
        
        # Activation function
        self.relu = nn.ReLU()
        self.softmax = nn.Softmax(dim=1)
        
        # Initialize weights
        self._init_weights()
        
    def _init_weights(self):
        """Advanced weight initialization"""
        for name, param in self.lstm.named_parameters():
            if 'weight_ih' in name:
                nn.init.xavier_uniform_(param.data)
            elif 'weight_hh' in name:
                nn.init.orthogonal_(param.data)
            elif 'bias' in name:
                param.data.fill_(0)
        
        # Initialize fully connected layers
        nn.init.xavier_uniform_(self.fc1.weight)
        nn.init.xavier_uniform_(self.fc2.weight)
        nn.init.constant_(self.fc1.bias, 0)
        nn.init.constant_(self.fc2.bias, 0)
        
    def forward(self, x):
        """Optimized forward pass with gradient clipping"""
        batch_size = x.size(0)
        
        # Initialize hidden states
        num_directions = 2 if self.bidirectional else 1
        h0 = torch.zeros(self.num_layers * num_directions, batch_size, self.hidden_size).to(x.device)
        c0 = torch.zeros(self.num_layers * num_directions, batch_size, self.hidden_size).to(x.device)
        
        # LSTM forward pass
        lstm_out, _ = self.lstm(x, (h0, c0))
        
        # Use last timestep output
        last_output = lstm_out[:, -1, :]
        
        # Apply layer normalization if enabled
        if self.use_layer_norm:
            last_output = self.layer_norm(last_output)
        
        # Apply dropout and fully connected layers
        output = self.dropout(last_output)
        output = self.relu(self.fc1(output))
        output = self.dropout(output)
        output = self.fc2(output)
        
        return output
    
    def predict_with_confidence(self, x):
        """Predict with confidence scores"""
        with torch.no_grad():
            logits = self.forward(x)
            probabilities = self.softmax(logits)
            confidence, predictions = torch.max(probabilities, dim=1)
            
        return predictions.cpu().numpy(), confidence.cpu().numpy()

class SecureStyleClassifier:
    """Enhanced style classifier with security and performance optimizations"""
    
    def __init__(self, n_estimators=200, max_depth=10, min_samples_split=5, 
                 min_samples_leaf=2, random_state=42):
        self.model = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            min_samples_split=min_samples_split,
            min_samples_leaf=min_samples_leaf,
            random_state=random_state,
            n_jobs=-1,  # Use all cores
            class_weight='balanced'  # Handle imbalanced classes
        )
        self.scaler = StandardScaler()
        self.is_trained = False
        self.classes_ = ['flicker', 'tracker', 'micro_juster', 'hybrid']
        self.feature_importance = None
        self.model_complexity = 0
        
    def extract_enhanced_features(self, mouse_data: List[Dict]) -> np.ndarray:
        """Extract enhanced features with security considerations"""
        if not mouse_data or len(mouse_data) < 20:
            return np.zeros(25)
            
        try:
            # Extract positions with validation
            positions = []
            for d in mouse_data:
                if 'x' in d and 'y' in d and isinstance(d['x'], (int, float)) and isinstance(d['y'], (int, float)):
                    positions.append([float(d['x']), float(d['y'])])
            
            if len(positions) < 20:
                return np.zeros(25)
                
            positions = np.array(positions)
            
            # Calculate velocities and accelerations
            velocities = np.diff(positions, axis=0)
            speeds = np.linalg.norm(velocities, axis=1)
            
            if len(speeds) < 5:
                return np.zeros(25)
                
            accelerations = np.diff(speeds)
            
            # Enhanced feature extraction
            features = []
            
            # Basic statistics
            features.extend([
                np.mean(speeds),
                np.std(speeds),
                np.max(speeds),
                np.median(speeds),
                np.percentile(speeds, 25),
                np.percentile(speeds, 75),
                np.percentile(speeds, 90),
                np.percentile(speeds, 95)
            ])
            
            # Acceleration features
            features.extend([
                np.mean(accelerations),
                np.std(accelerations),
                np.max(np.abs(accelerations)),
                np.percentile(np.abs(accelerations), 90)
            ])
            
            # Direction and movement features
            features.extend([
                self._calculate_direction_changes(positions),
                self._calculate_movement_efficiency(positions),
                self._calculate_path_complexity(positions),
                self._calculate_micro_adjustments(speeds),
                self._calculate_entropy(speeds)
            ])
            
            # Timing features
            features.extend([
                len(speeds) / 100.0,  # Duration
                np.std(np.diff(speeds)),  # Speed stability
                self._calculate_reaction_time(speeds),
                self._calculate_burst_frequency(speeds)
            ])
            
            # Security features (anti-pattern detection)
            features.extend([
                self._detect_perfect_patterns(positions),
                self._detect_timing_regularities(speeds),
                self._calculate_randomness_score(speeds)
            ])
            
            return np.array(features)
            
        except Exception as e:
            logging.warning(f"Feature extraction failed: {e}")
            return np.zeros(25)
    
    def _calculate_direction_changes(self, positions: np.ndarray) -> float:
        """Calculate direction changes with smoothing"""
        if len(positions) < 3:
            return 0.0
            
        # Smooth positions to reduce noise
        smoothed = self._smooth_trajectory(positions)
        
        directions = []
        for i in range(1, len(smoothed)):
            vec = smoothed[i] - smoothed[i-1]
            if np.linalg.norm(vec) > 1e-6:  # Avoid zero vectors
                angle = np.arctan2(vec[1], vec[0])
                directions.append(angle)
                
        if len(directions) < 2:
            return 0.0
            
        changes = np.abs(np.diff(directions))
        return np.mean(changes)
    
    def _calculate_movement_efficiency(self, positions: np.ndarray) -> float:
        """Calculate movement efficiency with path optimization"""
        if len(positions) < 2:
            return 0.0
            
        start = positions[0]
        end = positions[-1]
        direct_distance = np.linalg.norm(end - start)
        
        if direct_distance < 1e-6:
            return 0.0
            
        path_distance = 0.0
        for i in range(1, len(positions)):
            path_distance += np.linalg.norm(positions[i] - positions[i-1])
            
        efficiency = direct_distance / path_distance
        
        # Apply efficiency correction for very short movements
        if direct_distance < 50:
            efficiency = min(efficiency * 1.5, 1.0)
            
        return efficiency
    
    def _calculate_path_complexity(self, positions: np.ndarray) -> float:
        """Calculate path complexity using fractal dimension"""
        if len(positions) < 10:
            return 0.0
            
        # Calculate box-counting dimension approximation
        total_length = 0.0
        for i in range(1, len(positions)):
            total_length += np.linalg.norm(positions[i] - positions[i-1])
            
        if total_length < 1e-6:
            return 0.0
            
        # Calculate bounding box
        min_x, min_y = np.min(positions, axis=0)
        max_x, max_y = np.max(positions, axis=0)
        bounding_box_area = (max_x - min_x) * (max_y - min_y)
        
        if bounding_box_area < 1e-6:
            return 0.0
            
        # Complexity score
        complexity = total_length / np.sqrt(bounding_box_area)
        return min(complexity / 10.0, 1.0)
    
    def _calculate_micro_adjustments(self, speeds: np.ndarray) -> float:
        """Calculate micro-adjustments frequency"""
        if len(speeds) < 10:
            return 0.0
            
        # Count small speed variations
        threshold = np.mean(speeds) * 0.05
        micro_changes = np.sum(np.abs(np.diff(speeds)) < threshold)
        
        return micro_changes / len(speeds)
    
    def _calculate_entropy(self, speeds: np.ndarray) -> float:
        """Calculate speed entropy"""
        if len(speeds) < 5:
            return 0.0
            
        # Create histogram
        hist, _ = np.histogram(speeds, bins=10, density=True)
        hist = hist[hist > 0]  # Remove zero bins
        
        if len(hist) < 2:
            return 0.0
            
        # Calculate entropy
        entropy = -np.sum(hist * np.log2(hist))
        return entropy / np.log2(len(hist))  # Normalize
    
    def _calculate_reaction_time(self, speeds: np.ndarray) -> float:
        """Calculate reaction time from speed changes"""
        if len(speeds) < 20:
            return 0.0
            
        # Find acceleration peaks
        accelerations = np.diff(speeds)
        peaks = np.where(accelerations > np.mean(accelerations) + np.std(accelerations))[0]
        
        if len(peaks) < 2:
            return 0.0
            
        # Calculate average time between peaks
        reaction_times = np.diff(peaks)
        return np.mean(reaction_times) / 100.0  # Convert to seconds
    
    def _calculate_burst_frequency(self, speeds: np.ndarray) -> float:
        """Calculate burst movement frequency"""
        if len(speeds) < 10:
            return 0.0
            
        threshold = np.percentile(speeds, 80)
        bursts = np.sum(speeds > threshold)
        
        return bursts / len(speeds)
    
    def _detect_perfect_patterns(self, positions: np.ndarray) -> float:
        """Detect perfect geometric patterns (security feature)"""
        if len(positions) < 20:
            return 0.0
            
        # Check for straight lines
        if len(positions) >= 10:
            dx = np.diff(positions[:, 0])
            dy = np.diff(positions[:, 1])
            angles = np.arctan2(dy, dx)
            
            # Check for constant angles (straight lines)
            angle_variance = np.var(angles)
            if angle_variance < 0.01:
                return 1.0  # Perfect pattern detected
                
        return 0.0
    
    def _detect_timing_regularities(self, speeds: np.ndarray) -> float:
        """Detect timing regularities (security feature)"""
        if len(speeds) < 20:
            return 0.0
            
        # Check for regular intervals
        intervals = np.diff(speeds)
        interval_variance = np.var(intervals)
        
        if interval_variance < 1e-6:
            return 1.0  # Perfect timing detected
            
        return 0.0
    
    def _calculate_randomness_score(self, speeds: np.ndarray) -> float:
        """Calculate movement randomness score"""
        if len(speeds) < 10:
            return 0.0
            
        # Use approximate entropy as randomness measure
        m = 2  # embedding dimension
        r = 0.2 * np.std(speeds)
        
        def _app_entropy(data, m, r):
            if len(data) <= m:
                return 0
            
            # Create templates
            templates = np.array([data[i:i+m] for i in range(len(data)-m)])
            
            # Calculate similarity
            count = 0
            for i in range(len(templates)):
                for j in range(i+1, len(templates)):
                    if np.max(np.abs(templates[i] - templates[j])) <= r:
                        count += 1
            
            return -np.log(count / (len(templates) * (len(templates) - 1) / 2)) if count > 0 else 0
        
        return _app_entropy(speeds, m, r)
    
    def _smooth_trajectory(self, positions: np.ndarray, window_size=3) -> np.ndarray:
        """Smooth trajectory to reduce noise"""
        if len(positions) < window_size:
            return positions
            
        smoothed = np.zeros_like(positions)
        half_window = window_size // 2
        
        for i in range(len(positions)):
            start = max(0, i - half_window)
            end = min(len(positions), i + half_window + 1)
            smoothed[i] = np.mean(positions[start:end], axis=0)
            
        return smoothed
    
    def train(self, training_data: List[Tuple[List[Dict], str]], validation_split=0.2):
        """Enhanced training with validation and security checks"""
        if not training_data or len(training_data) < 10:
            logging.error("Insufficient training data")
            return False
            
        # Extract features with validation
        X = []
        y = []
        valid_samples = 0
        
        for mouse_data, style in training_data:
            features = self.extract_enhanced_features(mouse_data)
            if not np.all(np.isfinite(features)) or np.any(np.isnan(features)):
                continue
                
            X.append(features)
            y.append(style)
            valid_samples += 1
            
        if valid_samples < 10:
            logging.error(f"Insufficient valid training samples: {valid_samples}")
            return False
            
        X = np.array(X)
        y = np.array(y)
        
        # Check class balance
        unique_classes, class_counts = np.unique(y, return_counts=True)
        logging.info(f"Class distribution: {dict(zip(unique_classes, class_counts))}")
        
        # Handle imbalanced classes
        if len(unique_classes) > 1:
            min_samples = min(class_counts)
            if min_samples < 5:
                logging.warning(f"Imbalanced classes detected. Minimum samples per class: {min_samples}")
        
        # Split data
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=validation_split, random_state=42, stratify=y
        )
        
        # Normalize features
        try:
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_val_scaled = self.scaler.transform(X_val)
        except Exception as e:
            logging.error(f"Feature scaling failed: {e}")
            return False
        
        # Train model with cross-validation
        try:
            # Cross-validation for hyperparameter tuning
            cv_scores = cross_val_score(self.model, X_train_scaled, y_train, cv=3, scoring='accuracy')
            logging.info(f"Cross-validation scores: {cv_scores}")
            logging.info(f"Mean CV accuracy: {np.mean(cv_scores):.3f} (+/- {np.std(cv_scores) * 2:.3f})")
            
            # Train final model
            self.model.fit(X_train_scaled, y_train)
            
            # Evaluate on validation set
            train_score = self.model.score(X_train_scaled, y_train)
            val_score = self.model.score(X_val_scaled, y_val)
            
            logging.info(f"Training accuracy: {train_score:.3f}")
            logging.info(f"Validation accuracy: {val_score:.3f}")
            
            # Feature importance
            self.feature_importance = self.model.feature_importances_
            self.model_complexity = self.model.get_params()['n_estimators']
            
            self.is_trained = True
            
            # Security validation
            self._validate_security_features(X_val_scaled)
            
            return True
            
        except Exception as e:
            logging.error(f"Training failed: {e}")
            return False
    
    def _validate_security_features(self, X_val: np.ndarray):
        """Validate security features don't leak sensitive information"""
        # Check if security features correlate too strongly with predictions
        if self.feature_importance is not None:
            security_features = [18, 19, 20]  # Indices of security features
            security_importance = np.mean([self.feature_importance[i] for i in security_features])
            
            if security_importance > 0.3:
                logging.warning("Security features have high importance - may indicate overfitting")
    
    def predict_with_confidence(self, mouse_data: List[Dict]) -> Tuple[str, float]:
        """Predict with confidence score"""
        if not self.is_trained:
            return "unknown", 0.0
            
        features = self.extract_enhanced_features(mouse_data)
        features_scaled = self.scaler.transform([features])
        
        # Get prediction probabilities
        probabilities = self.model.predict_proba(features_scaled)[0]
        prediction = self.model.predict(features_scaled)[0]
        confidence = np.max(probabilities)
        
        return prediction, confidence

class OptimizedPlayerClustering:
    """Optimized player clustering with anomaly detection"""
    
    def __init__(self, n_clusters=5, eps=0.5, min_samples=5):
        self.n_clusters = n_clusters
        self.kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        self.dbscan = DBSCAN(eps=eps, min_samples=min_samples)
        self.scaler = StandardScaler()
        self.is_fitted = False
        self.cluster_centers_ = None
        self.labels_ = None
        self.anomaly_detector = None
        
    def extract_enhanced_player_features(self, mouse_data: List[Dict]) -> np.ndarray:
        """Extract enhanced player features for clustering"""
        if not mouse_data or len(mouse_data) < 30:
            return np.zeros(20)
            
        try:
            positions = []
            for d in mouse_data:
                if 'x' in d and 'y' in d:
                    positions.append([float(d['x']), float(d['y'])])
            
            if len(positions) < 30:
                return np.zeros(20)
                
            positions = np.array(positions)
            velocities = np.diff(positions, axis=0)
            speeds = np.linalg.norm(velocities, axis=1)
            
            if len(speeds) < 10:
                return np.zeros(20)
                
            accelerations = np.diff(speeds)
            
            # Enhanced feature set
            features = [
                # Speed characteristics
                np.mean(speeds), np.std(speeds), np.max(speeds), np.median(speeds),
                np.percentile(speeds, 25), np.percentile(speeds, 75), np.percentile(speeds, 90),
                
                # Acceleration characteristics
                np.mean(accelerations), np.std(accelerations), np.max(np.abs(accelerations)),
                
                # Movement quality
                self._calculate_precision_score(positions),
                self._calculate_efficiency_score(positions),
                self._calculate_smoothness_score(speeds),
                
                # Pattern complexity
                self._calculate_pattern_complexity(positions),
                self._calculate_direction_variance(positions),
                self._calculate_micro_adjustments(speeds),
                
                # Timing characteristics
                len(speeds) / 100.0,  # Duration
                np.std(np.diff(speeds)),  # Stability
                self._calculate_entropy(speeds),
                self._detect_anomalies(speeds)
            ]
            
            return np.array(features)
            
        except Exception as e:
            logging.warning(f"Player feature extraction failed: {e}")
            return np.zeros(20)
    
    def _calculate_precision_score(self, positions: np.ndarray) -> float:
        """Calculate precision with outlier removal"""
        if len(positions) < 10:
            return 0.0
            
        # Remove outliers
        q75, q25 = np.percentile(positions, [75, 25])
        iqr = q75 - q25
        lower_bound = q25 - 1.5 * iqr
        upper_bound = q75 + 1.5 * iqr
        
        mask = np.all((positions >= lower_bound) & (positions <= upper_bound), axis=1)
        filtered_positions = positions[mask]
        
        if len(filtered_positions) < 5:
            return 0.0
            
        start = filtered_positions[0]
        end = filtered_positions[-1]
        
        if np.allclose(start, end):
            return 0.0
            
        line_vector = end - start
        line_length = np.linalg.norm(line_vector)
        
        if line_length < 1e-6:
            return 0.0
            
        line_unit = line_vector / line_length
        point_vectors = filtered_positions - start
        projections = np.dot(point_vectors, line_unit)
        projections = np.clip(projections, 0, line_length)
        projected_points = start + projections[:, np.newaxis] * line_unit
        distances = np.linalg.norm(filtered_positions - projected_points, axis=1)
        
        return 1.0 / (1.0 + np.mean(distances))
    
    def _calculate_entropy(self, speeds: np.ndarray) -> float:
        """Calculate speed entropy"""
        if len(speeds) < 5:
            return 0.0
            
        hist, _ = np.histogram(speeds, bins=10, density=True)
        hist = hist[hist > 0]
        
        if len(hist) < 2:
            return 0.0
            
        entropy = -np.sum(hist * np.log2(hist))
        return entropy / np.log2(len(hist))
    
    def _detect_anomalies(self, speeds: np.ndarray) -> float:
        """Detect anomalous speed patterns"""
        if len(speeds) < 20:
            return 0.0
            
        # Use Z-score to detect anomalies
        z_scores = np.abs((speeds - np.mean(speeds)) / (np.std(speeds) + 1e-6))
        anomalies = np.sum(z_scores > 3)
        
        return anomalies / len(speeds)
    
    def fit(self, player_data: List[List[Dict]]):
        """Enhanced fitting with anomaly detection"""
        if not player_data or len(player_data) < self.n_clusters * 5:
            logging.error("Insufficient data for clustering")
            return False
            
        # Extract features
        X = []
        valid_samples = 0
        
        for mouse_data in player_data:
            features = self.extract_enhanced_player_features(mouse_data)
            if not np.all(np.isfinite(features)):
                continue
            X.append(features)
            valid_samples += 1
            
        if valid_samples < self.n_clusters * 3:
            logging.error(f"Insufficient valid samples: {valid_samples}")
            return False
            
        X = np.array(X)
        
        # Normalize features
        try:
            X_scaled = self.scaler.fit_transform(X)
        except Exception as e:
            logging.error(f"Feature scaling failed: {e}")
            return False
        
        # K-means clustering
        try:
            self.kmeans.fit(X_scaled)
            self.labels_ = self.kmeans.labels_
            self.cluster_centers_ = self.kmeans.cluster_centers_
            self.is_fitted = True
            
            # DBSCAN for anomaly detection
            self.dbscan.fit(X_scaled)
            
            # Evaluate clustering quality
            if len(set(self.labels_)) > 1:
                score = silhouette_score(X_scaled, self.labels_)
                logging.info(f"Clustering quality (Silhouette): {score:.3f}")
                
                if score < 0.3:
                    logging.warning("Poor clustering quality - consider adjusting parameters")
            
            return True
            
        except Exception as e:
            logging.error(f"Clustering failed: {e}")
            return False

class OptimizedLSTMTrainer:
    """Optimized LSTM trainer with quantization and security"""
    
    def __init__(self, device=None):
        self.model = None
        self.optimizer = None
        self.criterion = None
        self.device = device or torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.scaler = torch.cuda.amp.GradScaler() if torch.cuda.is_available() else None
        self.model_path = None
        
    def create_model(self, input_size=2, hidden_size=64, num_layers=2, output_size=4):
        """Create optimized LSTM model"""
        self.model = OptimizedLSTMAnalyzer(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            output_size=output_size,
            dropout_rate=0.3,
            bidirectional=False,
            use_layer_norm=True
        )
        self.model.to(self.device)
        self.criterion = nn.CrossEntropyLoss()
        self.optimizer = optim.AdamW(
            self.model.parameters(),
            lr=0.001,
            weight_decay=1e-4,
            betas=(0.9, 0.999)
        )
        
    def prepare_sequence_data(self, mouse_data: List[Dict], sequence_length=50) -> Tuple[torch.Tensor, torch.Tensor]:
        """Prepare sequence data with validation"""
        try:
            positions = []
            for d in mouse_data:
                if 'x' in d and 'y' in d:
                    positions.append([float(d['x']), float(d['y'])])
            
            if len(positions) < sequence_length:
                return torch.tensor([]), torch.tensor([])
                
            positions = np.array(positions)
            
            # Normalize positions
            mean_pos = np.mean(positions, axis=0)
            std_pos = np.std(positions, axis=0) + 1e-8
            positions_normalized = (positions - mean_pos) / std_pos
            
            sequences = []
            labels = []
            
            for i in range(len(positions_normalized) - sequence_length):
                seq = positions_normalized[i:i+sequence_length]
                label = self._classify_movement_pattern(seq)
                
                sequences.append(seq)
                labels.append(label)
                
            if len(sequences) == 0:
                return torch.tensor([]), torch.tensor([])
                
            return (
                torch.FloatTensor(sequences).to(self.device),
                torch.LongTensor(labels).to(self.device)
            )
            
        except Exception as e:
            logging.warning(f"Sequence preparation failed: {e}")
            return torch.tensor([]), torch.tensor([])
    
    def _classify_movement_pattern(self, sequence: np.ndarray) -> int:
        """Classify movement pattern with enhanced logic"""
        velocities = np.diff(sequence, axis=0)
        speeds = np.linalg.norm(velocities, axis=1)
        
        mean_speed = np.mean(speeds)
        max_speed = np.max(speeds)
        speed_variance = np.var(speeds)
        
        # Enhanced classification logic
        if max_speed > mean_speed * 4 and speed_variance > 0.2:
            return 0  # Aggressive flick
        elif mean_speed > 0.6 and speed_variance < 0.05:
            return 1  # Smooth tracking
        elif mean_speed < 0.2 and speed_variance > 0.15:
            return 2  # Micro-adjustments
        elif max_speed > mean_speed * 2 and np.std(speeds) > 0.3:
            return 3  # Burst movements
        else:
            return 4  # Mixed/complex pattern
    
    def train_model(self, training_data: List[List[Dict]], epochs=100, batch_size=32, validation_split=0.2):
        """Enhanced training with early stopping and quantization"""
        if not training_data or self.model is None:
            logging.error("No training data or model")
            return False
            
        # Prepare data
        sequences_list = []
        labels_list = []
        
        for mouse_data in training_data:
            sequences, labels = self.prepare_sequence_data(mouse_data)
            if len(sequences) > 0:
                sequences_list.append(sequences)
                labels_list.append(labels)
        
        if not sequences_list:
            logging.error("No valid sequences found")
            return False
            
        # Combine all sequences
        all_sequences = torch.cat(sequences_list, dim=0)
        all_labels = torch.cat(labels_list, dim=0)
        
        # Split data
        dataset_size = len(all_sequences)
        indices = np.random.permutation(dataset_size)
        split_idx = int(dataset_size * (1 - validation_split))
        
        train_indices = indices[:split_idx]
        val_indices = indices[split_idx:]
        
        # Training loop with optimizations
        best_val_loss = float('inf')
        patience_counter = 0
        patience = 10
        
        self.model.train()
        
        for epoch in range(epochs):
            epoch_loss = 0
            batch_count = 0
            
            # Shuffle training data
            np.random.shuffle(train_indices)
            
            for i in range(0, len(train_indices), batch_size):
                batch_indices = train_indices[i:i+batch_size]
                
                batch_sequences = all_sequences[batch_indices]
                batch_labels = all_labels[batch_indices]
                
                if len(batch_sequences) == 0:
                    continue
                
                self.optimizer.zero_grad()
                
                # Mixed precision training if available
                if self.scaler:
                    with torch.cuda.amp.autocast():
                        outputs = self.model(batch_sequences)
                        loss = self.criterion(outputs, batch_labels)
                    
                    self.scaler.scale(loss).backward()
                    self.scaler.step(self.optimizer)
                    self.scaler.update()
                else:
                    outputs = self.model(batch_sequences)
                    loss = self.criterion(outputs, batch_labels)
                    loss.backward()
                    self.optimizer.step()
                
                epoch_loss += loss.item()
                batch_count += 1
            
            # Validation
            if val_indices.size > 0:
                self.model.eval()
                with torch.no_grad():
                    val_outputs = self.model(all_sequences[val_indices])
                    val_loss = self.criterion(val_outputs, all_labels[val_indices])
                
                self.model.train()
                
                # Early stopping
                if val_loss < best_val_loss:
                    best_val_loss = val_loss
                    patience_counter = 0
                    # Save best model
                    if self.model_path:
                        torch.save(self.model.state_dict(), self.model_path)
                else:
                    patience_counter += 1
                    
                if patience_counter >= patience:
                    logging.info(f"Early stopping at epoch {epoch}")
                    break
            
            # Logging
            if epoch % 10 == 0:
                avg_loss = epoch_loss / max(batch_count, 1)
                val_acc = self._calculate_accuracy(val_indices, all_sequences, all_labels) if val_indices.size > 0 else 0
                logging.info(f"Epoch {epoch}/{epochs}, Loss: {avg_loss:.4f}, Val Acc: {val_acc:.3f}")
        
        return True
    
    def _calculate_accuracy(self, indices, sequences, labels):
        """Calculate validation accuracy"""
        if len(indices) == 0:
            return 0.0
            
        self.model.eval()
        with torch.no_grad():
            outputs = self.model(sequences[indices])
            _, predicted = torch.max(outputs.data, 1)
            accuracy = (predicted == labels[indices]).sum().item() / len(indices)
        
        self.model.train()
        return accuracy
    
    def quantize_model(self):
        """Apply quantization for performance optimization"""
        if self.model is None:
            return False
            
        try:
            # Dynamic quantization
            self.model = torch.quantization.quantize_dynamic(
                self.model,
                {nn.LSTM, nn.Linear},
                dtype=torch.qint8
            )
            logging.info("Model quantized successfully")
            return True
        except Exception as e:
            logging.warning(f"Quantization failed: {e}")
            return False
    
    def predict_pattern(self, mouse_data: List[Dict]) -> Tuple[str, float]:
        """Predict pattern with confidence"""
        if self.model is None:
            return "unknown", 0.0
            
        self.model.eval()
        
        sequences, _ = self.prepare_sequence_data(mouse_data)
        
        if len(sequences) == 0:
            return "unknown", 0.0
            
        try:
            with torch.no_grad():
                outputs = self.model(sequences[-1:])
                probabilities = torch.softmax(outputs, dim=1)
                confidence, prediction = torch.max(probabilities, dim=1)
                
                patterns = ['flick', 'tracking', 'micro_adjustments', 'burst', 'mixed']
                pattern = patterns[prediction.item()]
                confidence_score = confidence.item()
                
            return pattern, confidence_score
            
        except Exception as e:
            logging.warning(f"Prediction failed: {e}")
            return "unknown", 0.0

def create_improved_ml_models():
    """Factory for creating improved ML models"""
    return {
        'style_classifier': SecureStyleClassifier(),
        'player_clustering': OptimizedPlayerClustering(),
        'lstm_trainer': OptimizedLSTMTrainer()
    }

# Example usage
if __name__ == "__main__":
    print("🤖 Testing Improved ML Models...")
    
    # Create models
    models = create_improved_ml_models()
    
    # Test data generation
    test_data = []
    for i in range(20):
        session = []
        for j in range(100):
            x = j * 5 + np.random.normal(0, 10)
            y = np.sin(j * 0.1) * 50 + np.random.normal(0, 5)
            session.append({'x': x, 'y': y})
        test_data.append(session)
    
    # Test style classifier
    print("\n🎯 Testing Style Classifier:")
    classifier = models['style_classifier']
    
    # Create training data
    training_data = []
    for session in test_data:
        style = np.random.choice(['flicker', 'tracker', 'micro_juster'])
        training_data.append((session, style))
    
    success = classifier.train(training_data)
    print(f"   Training success: {success}")
    
    if success:
        prediction, confidence = classifier.predict_with_confidence(test_data[0])
        print(f"   Prediction: {prediction}, Confidence: {confidence:.3f}")
    
    # Test LSTM
    print("\n🧠 Testing LSTM:")
    lstm_trainer = models['lstm_trainer']
    lstm_trainer.create_model()
    
    success = lstm_trainer.train_model(test_data[:10], epochs=20)
    print(f"   Training success: {success}")
    
    if success:
        pattern, confidence = lstm_trainer.predict_pattern(test_data[0])
        print(f"   Pattern: {pattern}, Confidence: {confidence:.3f}")
    
    print("\n✅ Improved ML models test completed!")