#!/usr/bin/env python3
"""
MouseAI Visualization - Визуализация данных и графики
"""

from .heatmaps import create_heatmap_generator
from .dashboard import create_dashboard
# from .visualizer_3d import create_3d_visualizer

__all__ = [
    'create_heatmap_generator',
    'create_dashboard'
]
