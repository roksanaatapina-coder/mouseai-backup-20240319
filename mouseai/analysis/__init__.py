#!/usr/bin/env python3
"""
MouseAI Analysis - Научный анализ движений мыши
"""

from .scientific_metrics import create_scientific_metrics
from .ml_models import create_ml_models
# from .biomechanics import create_biomechanics_analyzer

__all__ = [
    'create_scientific_metrics',
    'create_ml_models'
]
