#!/usr/bin/env python3
"""
MouseAI Analysis Report Generator
Analyzes all saved match records and generates comprehensive insights.
"""

import json
import os
import glob
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional, Union

class MouseAnalysisReport:
    def __init__(self, sessions_dir: str = "../myapp/sessions") -> None:
        self.sessions_dir: Path = Path(sessions_dir)
        self.matches: List[Dict[str, Any]] = []
        self.load_all_matches()
    
    def load_all_matches(self) -> None:
        """Load all session files from the sessions directory."""
        session_files = list(self.sessions_dir.glob("session_*.json"))
        session_files.sort()  # Sort by filename (chronological order)
        
        for file_path in session_files:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    self.matches.append(data)
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
        
        print(f"Loaded {len(self.matches)} matches for analysis")
    
    def calculate_progress(self) -> Tuple[Dict[str, str], Dict[str, float]]:
        """Calculate progress from first to last match."""
        if len(self.matches) < 2:
            return {}, {}
        
        first = self.matches[0]
        last = self.matches[-1]
        
        progress = {
            'duration': f"{first['duration_seconds']:.1f}s → {last['duration_seconds']:.1f}s",
            'activity': f"{first['movement_activity']} → {last['movement_activity']}",
            'avg_magnitude': f"{first['average_movement_magnitude']:.2f} → {last['average_movement_magnitude']:.2f}",
            'variability': f"{first['movement_variability']:.2f} → {last['movement_variability']:.2f}",
            'intensity': f"{first['intensity_score']:.2f} → {last['intensity_score']:.2f}",
            'stability': f"{first['stability_score']:.2f} → {last['stability_score']:.2f}"
        }
        
        # Calculate percentage changes
        def safe_pct(old, new):
            return ((new - old) / old * 100) if old != 0 else 0

        changes = {
            'duration_change': safe_pct(first['duration_seconds'], last['duration_seconds']),
            'activity_change': safe_pct(first['movement_activity'], last['movement_activity']),
            'magnitude_change': safe_pct(first['average_movement_magnitude'], last['average_movement_magnitude']),
            'variability_change': safe_pct(first['movement_variability'], last['movement_variability']),
            'stability_change': safe_pct(first['stability_score'], last['stability_score'])
        }
        
        return progress, changes
    
    def analyze_trends(self) -> Tuple[Dict[str, float], Dict[str, str]]:
        """Analyze trends across all matches."""
        if len(self.matches) < 3:
            return {}, {}
        
        # Extract time series data
        durations = [m['duration_seconds'] for m in self.matches]
        activities = [m['movement_activity'] for m in self.matches]
        magnitudes = [m['average_movement_magnitude'] for m in self.matches]
        variabilities = [m['movement_variability'] for m in self.matches]
        intensities = [m['intensity_score'] for m in self.matches]
        stabilities = [m['stability_score'] for m in self.matches]
        
        # Calculate trends (simple linear regression slope)
        def calculate_trend(values: List[float]) -> float:
            n = len(values)
            x = list(range(n))
            x_mean = sum(x) / n
            y_mean = sum(values) / n
            
            numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
            denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
            
            if denominator == 0:
                return 0
            return numerator / denominator
        
        trends = {
            'duration_trend': calculate_trend(durations),
            'activity_trend': calculate_trend(activities),
            'magnitude_trend': calculate_trend(magnitudes),
            'variability_trend': calculate_trend(variabilities),
            'intensity_trend': calculate_trend(intensities),
            'stability_trend': calculate_trend(stabilities)
        }
        
        # Interpret trends
        interpretations = {}
        for metric, trend in trends.items():
            if abs(trend) < 0.1:  # Threshold for "stable"
                interpretations[metric] = "stable"
            elif trend > 0:
                interpretations[metric] = "improving" if metric in ['stability_trend', 'intensity_trend'] else "increasing"
            else:
                interpretations[metric] = "declining" if metric in ['stability_trend', 'intensity_trend'] else "decreasing"
        
        return trends, interpretations
    
    def calculate_overall_stats(self) -> Dict[str, Any]:
        """Calculate overall statistics across all matches."""
        if not self.matches:
            return {}
        
        stats: Dict[str, Any] = {
            'total_matches': len(self.matches),
            'total_duration': sum(m['duration_seconds'] for m in self.matches),
            'avg_duration': sum(m['duration_seconds'] for m in self.matches) / len(self.matches),
            'total_activity': sum(m['movement_activity'] for m in self.matches),
            'avg_activity': sum(m['movement_activity'] for m in self.matches) / len(self.matches),
            'avg_magnitude': sum(m['average_movement_magnitude'] for m in self.matches) / len(self.matches),
            'avg_variability': sum(m['movement_variability'] for m in self.matches) / len(self.matches),
            'avg_intensity': sum(m['intensity_score'] for m in self.matches) / len(self.matches),
            'avg_stability': sum(m['stability_score'] for m in self.matches) / len(self.matches),
            'games_played': list(set(m['selected_game'] for m in self.matches))
        }
        
        # Calculate style distribution
        styles = [m['movement_style'] for m in self.matches]
        style_counts = {}
        for style in styles:
            style_counts[style] = style_counts.get(style, 0) + 1
        
        stats['style_distribution'] = style_counts
        
        # Calculate stability distribution
        stability_labels = [m['stability_label'] for m in self.matches]
        stability_counts = {}
        for label in stability_labels:
            stability_counts[label] = stability_counts.get(label, 0) + 1
        
        stats['stability_distribution'] = stability_counts
        
        return stats
    
    def generate_recommendations(self) -> List[str]:
        """Generate personalized recommendations based on all data."""
        if not self.matches:
            return ["No data available for recommendations"]
        
        stats = self.calculate_overall_stats()
        trends, interpretations = self.analyze_trends() if len(self.matches) >= 3 else ({}, {})
        
        recommendations = []
        
        # Analyze stability
        if stats['avg_stability'] < 0.7:
            recommendations.append("🎯 Focus on stability: Your average stability score is low. Practice micro-adjustments with slower, more controlled movements.")
        elif stats['avg_stability'] > 0.8:
            recommendations.append("🎯 Stability is good: Your movement control is solid. Maintain this consistency.")
        
        # Analyze variability
        if stats['avg_variability'] > 15:
            recommendations.append("🎯 Reduce jitter: High movement variability indicates inconsistent control. Try to relax your grip and use smoother wrist movements.")
        elif stats['avg_variability'] < 5:
            recommendations.append("🎯 Consistency achieved: Low variability shows good control. Consider working on dynamic movements.")
        
        # Analyze trends
        if len(self.matches) >= 3:
            if interpretations.get('stability_trend') == 'improving':
                recommendations.append("📈 Trending positive: Your stability is improving over time. Keep up the good work!")
            elif interpretations.get('stability_trend') == 'declining':
                recommendations.append("📉 Attention needed: Your stability is declining. Review your grip and posture.")
            
            if interpretations.get('variability_trend') == 'decreasing':
                recommendations.append("📈 Consistency improving: Your movement variability is decreasing. This is a positive trend!")
        
        # Analyze session length
        if stats['avg_duration'] < 30:
            recommendations.append("⏱️ Session length: Consider longer sessions (30+ seconds) for more meaningful data collection.")
        
        # Analyze style consistency
        if len(stats['style_distribution']) > 2:
            recommendations.append("🎯 Style consistency: You show varied movement styles. Try to identify which style works best for your game.")
        
        # Game-specific recommendations
        if 'Universal' in stats['games_played']:
            recommendations.append("🎮 Game selection: Consider testing with specific game profiles (CS2, Valorant, etc.) for more targeted analysis.")
        
        # General performance
        if stats['avg_intensity'] == 1.0:
            recommendations.append("🔥 High intensity: You maintain high movement intensity. Ensure this doesn't compromise accuracy.")
        
        return recommendations
    
    def generate_report(self) -> None:
        """Generate the complete analysis report."""
        print("=" * 80)
        print("MOUSEAI ANALYSIS REPORT")
        print("=" * 80)
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total matches analyzed: {len(self.matches)}")
        print()
        
        # Progress Analysis
        print("📊 PROGRESS ANALYSIS")
        print("-" * 40)
        if len(self.matches) >= 2:
            progress, changes = self.calculate_progress()
            for metric, value in progress.items():
                print(f"{metric.upper()}: {value}")
            
            print("\nPercentage changes:")
            for metric, change in changes.items():
                direction = "↑" if change > 0 else "↓" if change < 0 else "→"
                print(f"{metric.replace('_change', '').upper()}: {change:+.1f}% {direction}")
        else:
            print("Need at least 2 matches to show progress")
        print()
        
        # Trends Analysis
        print("📈 TRENDS ANALYSIS")
        print("-" * 40)
        if len(self.matches) >= 3:
            trends, interpretations = self.analyze_trends()
            for metric, interpretation in interpretations.items():
                metric_name = metric.replace('_trend', '').replace('_', ' ').title()
                print(f"{metric_name}: {interpretation}")
        else:
            print("Need at least 3 matches to show trends")
        print()
        
        # Overall Statistics
        print("📈 OVERALL STATISTICS")
        print("-" * 40)
        stats = self.calculate_overall_stats()
        print(f"Total matches: {stats['total_matches']}")
        print(f"Total duration: {stats['total_duration']:.1f}s")
        print(f"Average duration: {stats['avg_duration']:.1f}s")
        print(f"Average activity: {stats['avg_activity']:.0f}")
        print(f"Average magnitude: {stats['avg_magnitude']:.2f}")
        print(f"Average variability: {stats['avg_variability']:.2f}")
        print(f"Average intensity: {stats['avg_intensity']:.2f}")
        print(f"Average stability: {stats['avg_stability']:.2f}")
        print(f"Games played: {', '.join(stats['games_played'])}")
        print()
        print("Movement style distribution:")
        for style, count in stats['style_distribution'].items():
            percentage = (count / stats['total_matches']) * 100
            print(f"  {style}: {count} ({percentage:.1f}%)")
        print()
        print("Stability distribution:")
        for label, count in stats['stability_distribution'].items():
            percentage = (count / stats['total_matches']) * 100
            print(f"  {label}: {count} ({percentage:.1f}%)")
        print()
        
        # Recommendations
        print("🎯 PERSONALIZED RECOMMENDATIONS")
        print("-" * 40)
        recommendations = self.generate_recommendations()
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec}")
        print()
        
        # Individual Match Details
        print("📋 INDIVIDUAL MATCH DETAILS")
        print("-" * 40)
        for i, match in enumerate(self.matches, 1):
            print(f"Match {i} ({match['selected_game']}):")
            print(f"  Duration: {match['duration_seconds']:.1f}s")
            print(f"  Activity: {match['movement_activity']}")
            print(f"  Style: {match['movement_style']}")
            print(f"  Stability: {match['stability_label']}")
            print(f"  Intensity: {match['intensity_score']:.2f}")
            print(f"  Stability: {match['stability_score']:.2f}")
            print()
        
        print("=" * 80)
        print("END OF REPORT")
        print("=" * 80)

if __name__ == "__main__":
    analyzer = MouseAnalysisReport()
    analyzer.generate_report()