#!/usr/bin/env python3
"""
Dashboard - Интерактивные графики прогресса
"""

import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from typing import Dict, List, Optional, Tuple
import numpy as np
from datetime import datetime, timedelta
import pandas as pd

class ProgressDashboard:
    """Интерактивная панель прогресса"""
    
    def __init__(self):
        self.session_history = []
        self.player_stats = {}
        
    def add_session(self, session_data: Dict):
        """Добавить сессию в историю"""
        self.session_history.append({
            'timestamp': datetime.now(),
            'game': session_data.get('game', 'Unknown'),
            'duration': session_data.get('duration', 0),
            'metrics': session_data.get('metrics', {}),
            'style': session_data.get('style', 'unknown')
        })
        
        # Обновляем статистику игрока
        self._update_player_stats(session_data)
        
    def _update_player_stats(self, session_data: Dict):
        """Обновить статистику игрока"""
        if 'metrics' not in session_data:
            return
            
        metrics = session_data['metrics']
        
        # Обновляем средние показатели
        if 'avg_sample_entropy' not in self.player_stats:
            self.player_stats = {
                'avg_sample_entropy': [],
                'avg_mad': [],
                'avg_ttpv': [],
                'avg_efficiency': [],
                'session_count': 0
            }
            
        self.player_stats['avg_sample_entropy'].append(metrics.get('sample_entropy', 0))
        self.player_stats['avg_mad'].append(metrics.get('maximum_absolute_deviation', 0))
        self.player_stats['avg_ttpv'].append(metrics.get('time_to_peak_velocity', 0))
        self.player_stats['avg_efficiency'].append(metrics.get('movement_efficiency', 0))
        self.player_stats['session_count'] += 1
        
    def create_progress_over_time(self) -> go.Figure:
        """Создать график прогресса во времени"""
        
        if not self.session_history:
            return go.Figure()
            
        # Подготавливаем данные
        dates = [session['timestamp'] for session in self.session_history]
        durations = [session['duration'] for session in self.session_history]
        
        # Рассчитываем скользящее среднее
        window_size = min(5, len(durations))
        if window_size > 1:
            durations_ma = np.convolve(durations, np.ones(window_size)/window_size, mode='valid')
            dates_ma = dates[window_size-1:]
        else:
            durations_ma = durations
            dates_ma = dates
            
        # Создаем график
        fig = go.Figure()
        
        # Добавляем исходные данные
        fig.add_trace(go.Scatter(
            x=dates,
            y=durations,
            mode='markers',
            name='Сессии',
            marker=dict(size=8, color='lightblue'),
            hovertemplate='Дата: %{x}<br>Длительность: %{y:.1f} сек<extra></extra>'
        ))
        
        # Добавляем скользящее среднее
        fig.add_trace(go.Scatter(
            x=dates_ma,
            y=durations_ma,
            mode='lines',
            name=f'Скользящее среднее ({window_size})',
            line=dict(color='blue', width=3),
            hovertemplate='Дата: %{x}<br>Средняя длительность: %{y:.1f} сек<extra></extra>'
        ))
        
        # Настройки графика
        fig.update_layout(
            title='Прогресс: Длительность сессий во времени',
            xaxis_title='Дата',
            yaxis_title='Длительность (сек)',
            hovermode='x unified',
            width=1000,
            height=500
        )
        
        return fig
        
    def create_metrics_comparison(self) -> go.Figure:
        """Создать график сравнения метрик"""
        
        if not self.player_stats or self.player_stats['session_count'] < 2:
            return go.Figure()
            
        # Рассчитываем средние значения
        avg_entropy = np.mean(self.player_stats['avg_sample_entropy'])
        avg_mad = np.mean(self.player_stats['avg_mad'])
        avg_ttpv = np.mean(self.player_stats['avg_ttpv'])
        avg_efficiency = np.mean(self.player_stats['avg_efficiency'])
        
        # Нормализуем значения для радарного графика
        # Чем выше эффективность и энтропия - тем лучше
        # Чем ниже MAD и TTPV - тем лучше
        normalized_values = [
            avg_entropy,  # Энтропия (чем выше, тем лучше)
            1.0 / (1.0 + avg_mad),  # MAD (чем ниже, тем лучше)
            1.0 / (1.0 + avg_ttpv),  # TTPV (чем ниже, тем лучше)
            avg_efficiency,  # Эффективность (чем выше, тем лучше)
            1.0 / (1.0 + np.std(self.player_stats['avg_sample_entropy']))  # Стабильность
        ]
        
        categories = ['Сложность', 'Точность', 'Реакция', 'Эффективность', 'Стабильность']
        
        # Создаем радарный график
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=normalized_values + [normalized_values[0]],  # Замыкаем круг
            theta=categories + [categories[0]],
            fill='toself',
            name='Ваш прогресс',
            line_color='blue'
        ))
        
        # Добавляем идеальный профиль
        ideal_values = [0.8, 0.9, 0.9, 0.9, 0.9]
        fig.add_trace(go.Scatterpolar(
            r=ideal_values + [ideal_values[0]],
            theta=categories + [categories[0]],
            fill='none',
            name='Идеальный профиль',
            line=dict(color='red', dash='dash')
        ))
        
        # Настройки графика
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                )
            ),
            title='Радарный график прогресса',
            width=800,
            height=700
        )
        
        return fig
        
    def create_game_analysis(self) -> go.Figure:
        """Создать анализ по играм"""
        
        if not self.session_history:
            return go.Figure()
            
        # Группируем по играм
        game_stats = {}
        for session in self.session_history:
            game = session['game']
            if game not in game_stats:
                game_stats[game] = {
                    'durations': [],
                    'count': 0,
                    'avg_duration': 0
                }
                
            game_stats[game]['durations'].append(session['duration'])
            game_stats[game]['count'] += 1
            
        # Рассчитываем средние
        for game in game_stats:
            game_stats[game]['avg_duration'] = np.mean(game_stats[game]['durations'])
            
        # Сортируем по количеству сессий
        sorted_games = sorted(game_stats.items(), key=lambda x: x[1]['count'], reverse=True)
        
        if not sorted_games:
            return go.Figure()
            
        games = [item[0] for item in sorted_games]
        counts = [item[1]['count'] for item in sorted_games]
        avg_durations = [item[1]['avg_duration'] for item in sorted_games]
        
        # Создаем комбинированный график
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Количество сессий по играм', 'Средняя длительность по играм'),
            vertical_spacing=0.1
        )
        
        # График 1: Количество сессий
        fig.add_trace(
            go.Bar(
                x=games,
                y=counts,
                name='Количество сессий',
                marker_color='lightblue'
            ),
            row=1, col=1
        )
        
        # График 2: Средняя длительность
        fig.add_trace(
            go.Bar(
                x=games,
                y=avg_durations,
                name='Средняя длительность',
                marker_color='orange'
            ),
            row=2, col=1
        )
        
        # Настройки графика
        fig.update_layout(
            title='Анализ по играм',
            height=600,
            showlegend=False
        )
        
        return fig
        
    def create_style_evolution(self) -> go.Figure:
        """Создать график эволюции стиля игры"""
        
        if not self.session_history:
            return go.Figure()
            
        # Группируем по стилям
        style_counts = {}
        for session in self.session_history:
            style = session['style']
            if style not in style_counts:
                style_counts[style] = 0
            style_counts[style] += 1
            
        if not style_counts:
            return go.Figure()
            
        styles = list(style_counts.keys())
        counts = list(style_counts.values())
        
        # Создаем круговую диаграмму
        fig = go.Figure()
        
        fig.add_trace(go.Pie(
            labels=styles,
            values=counts,
            name="Стили игры",
            hole=0.3,
            hovertemplate='<b>%{label}</b><br>Сессий: %{value}<br>Процент: %{percent}<extra></extra>'
        ))
        
        # Настройки графика
        fig.update_layout(
            title='Распределение стилей игры',
            width=600,
            height=500
        )
        
        return fig
        
    def create_comprehensive_dashboard(self) -> Dict[str, go.Figure]:
        """Создать комплексную панель управления"""
        
        dashboard = {}
        
        # 1. Прогресс во времени
        dashboard['progress_over_time'] = self.create_progress_over_time()
        
        # 2. Сравнение метрик
        dashboard['metrics_comparison'] = self.create_metrics_comparison()
        
        # 3. Анализ по играм
        dashboard['game_analysis'] = self.create_game_analysis()
        
        # 4. Эволюция стиля
        dashboard['style_evolution'] = self.create_style_evolution()
        
        return dashboard
        
    def generate_dashboard_report(self, output_dir: str = "dashboard") -> Dict[str, str]:
        """Сгенерировать отчет панели управления"""
        
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        dashboard = self.create_comprehensive_dashboard()
        results = {}
        
        for name, fig in dashboard.items():
            filename = f"{output_dir}/{name}.html"
            fig.write_html(filename)
            results[name] = filename
            
        return results

class RealTimeDashboard:
    """Реальное время панель управления"""
    
    def __init__(self):
        self.current_session_data = []
        self.live_metrics = {}
        
    def update_live_data(self, mouse_data: Dict):
        """Обновить данные в реальном времени"""
        self.current_session_data.append(mouse_data)
        
        # Рассчитываем текущие метрики
        if len(self.current_session_data) > 10:
            self._calculate_live_metrics()
            
    def _calculate_live_metrics(self):
        """Рассчитать метрики в реальном времени"""
        if len(self.current_session_data) < 10:
            return
            
        # Простой расчет скорости
        recent_data = self.current_session_data[-10:]
        speeds = []
        
        for i in range(1, len(recent_data)):
            prev = recent_data[i-1]
            curr = recent_data[i]
            if all(k in prev and k in curr for k in ['x', 'y']):
                dx = curr['x'] - prev['x']
                dy = curr['y'] - prev['y']
                speed = (dx**2 + dy**2)**0.5
                speeds.append(speed)
                
        if speeds:
            self.live_metrics = {
                'current_speed': speeds[-1],
                'avg_speed': np.mean(speeds),
                'max_speed': max(speeds),
                'session_duration': len(self.current_session_data) * 0.01
            }
            
    def create_live_progress_chart(self) -> go.Figure:
        """Создать график прогресса в реальном времени"""
        
        fig = go.Figure()
        
        if self.live_metrics:
            # Создаем индикаторы
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('Текущая скорость', 'Средняя скорость', 'Максимальная скорость', 'Длительность'),
                specs=[[{"type": "indicator"}, {"type": "indicator"}],
                       [{"type": "indicator"}, {"type": "indicator"}]]
            )
            
            # Текущая скорость
            fig.add_trace(
                go.Indicator(
                    mode="gauge+number",
                    value=self.live_metrics.get('current_speed', 0),
                    title={'text': "Текущая скорость"},
                    gauge={'axis': {'range': [None, 100]},
                          'bar': {'color': "blue"},
                          'steps': [{'range': [0, 50], 'color': "lightgray"},
                                   {'range': [50, 100], 'color': "gray"}],
                          'threshold': {'line': {'color': "red", 'width': 4},
                                       'thickness': 0.75, 'value': 90}}
                ),
                row=1, col=1
            )
            
            # Средняя скорость
            fig.add_trace(
                go.Indicator(
                    mode="gauge+number",
                    value=self.live_metrics.get('avg_speed', 0),
                    title={'text': "Средняя скорость"},
                    gauge={'axis': {'range': [None, 100]},
                          'bar': {'color': "green"},
                          'steps': [{'range': [0, 50], 'color': "lightgray"},
                                   {'range': [50, 100], 'color': "gray"}]}
                ),
                row=1, col=2
            )
            
            # Максимальная скорость
            fig.add_trace(
                go.Indicator(
                    mode="gauge+number",
                    value=self.live_metrics.get('max_speed', 0),
                    title={'text': "Макс. скорость"},
                    gauge={'axis': {'range': [None, 100]},
                          'bar': {'color': "red"},
                          'steps': [{'range': [0, 50], 'color': "lightgray"},
                                   {'range': [50, 100], 'color': "gray"}]}
                ),
                row=2, col=1
            )
            
            # Длительность
            fig.add_trace(
                go.Indicator(
                    mode="number+gauge+delta",
                    value=self.live_metrics.get('session_duration', 0),
                    delta={'reference': 60},
                    title={'text': "Длительность (сек)"},
                    gauge={'axis': {'range': [None, 300]},
                          'bar': {'color': "orange"},
                          'steps': [{'range': [0, 100], 'color': "lightgray"},
                                   {'range': [100, 200], 'color': "gray"},
                                   {'range': [200, 300], 'color': "darkgray"}]}
                ),
                row=2, col=2
            )
            
        fig.update_layout(
            title='Live Dashboard - Реальное время мониторинг',
            height=500
        )
        
        return fig

def create_dashboard():
    """Фабрика для создания панели управления"""
    return ProgressDashboard()

def create_live_dashboard():
    """Фабрика для создания live панели"""
    return RealTimeDashboard()

# Пример использования
if __name__ == "__main__":
    print("📊 Тестирование Dashboard...")
    
    # Создаем тестовые данные
    dashboard = create_dashboard()
    
    # Добавляем тестовые сессии
    for i in range(10):
        session_data = {
            'game': np.random.choice(['CS2', 'PUBG', 'Valorant']),
            'duration': np.random.uniform(30, 300),
            'metrics': {
                'sample_entropy': np.random.uniform(0.2, 0.8),
                'maximum_absolute_deviation': np.random.uniform(10, 100),
                'time_to_peak_velocity': np.random.uniform(0.1, 0.5),
                'movement_efficiency': np.random.uniform(0.3, 0.9)
            },
            'style': np.random.choice(['flicker', 'tracker', 'micro_juster'])
        }
        dashboard.add_session(session_data)
        
    # Генерируем отчет
    results = dashboard.generate_dashboard_report("test_dashboard")
    
    print("📊 Сгенерированные отчеты:")
    for name, filepath in results.items():
        print(f"   {name}: {filepath}")
        
    print("\n✅ Dashboard успешно создан!")