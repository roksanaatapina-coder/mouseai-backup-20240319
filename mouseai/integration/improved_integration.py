#!/usr/bin/env python3
"""
Improved Integration - Enhanced integration module that combines all improved components
Based on AI Orchestra analysis recommendations for better architecture and performance
"""

import time
import threading
import asyncio
import logging
import json
import os
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from datetime import datetime
import numpy as np

# Import improved components
from mouseai.core.data_collector_improved import create_improved_data_collector, ImprovedDataCollector
from mouseai.analysis.ml_models_improved import create_improved_ml_models, OptimizedLSTMTrainer
from mouseai.analysis.scientific_metrics import ScientificMetricsCalculator, MetricsInterpreter
from mouseai.security.anti_ban_system import create_anti_ban_system, AntiBanSystem
from mouseai.utils.logger import setup_logging

@dataclass
class SessionConfig:
    """Enhanced session configuration"""
    sampling_rate: int = 100
    buffer_size: int = 10000
    enable_security: bool = True
    enable_performance: bool = True
    protection_level: str = "MEDIUM"
    auto_save_interval: int = 300  # seconds
    ml_model_path: str = "models/"
    encryption_enabled: bool = True

class EnhancedMouseAI:
    """Enhanced MouseAI with all improvements integrated"""
    
    def __init__(self, config: Optional[SessionConfig] = None):
        self.config = config or SessionConfig()
        
        # Initialize components
        self.data_collector = None
        self.ml_models = None
        self.scientific_metrics = None
        self.anti_ban_system = None
        self.metrics_interpreter = None
        
        # Session state
        self.is_recording = False
        self.session_start_time = None
        self.session_data = {}
        
        # Performance monitoring
        self.performance_stats = {
            'collection_rate': 0,
            'processing_time': 0,
            'memory_usage': 0,
            'security_violations': 0
        }
        
        # Async components
        self.async_loop = None
        self.background_tasks = []
        
        # Initialize system
        self._initialize_components()
        
        logging.info("🚀 Enhanced MouseAI system initialized")
    
    def _initialize_components(self):
        """Initialize all enhanced components"""
        try:
            # Initialize data collector
            self.data_collector = create_improved_data_collector()
            self.data_collector.sampling_rate = self.config.sampling_rate
            self.data_collector.buffer_size = self.config.buffer_size
            self.data_collector.enable_security = self.config.enable_security
            self.data_collector.enable_performance = self.config.enable_performance
            
            # Initialize ML models
            self.ml_models = create_improved_ml_models()
            
            # Initialize scientific metrics
            self.scientific_metrics = ScientificMetricsCalculator(
                sampling_rate=self.config.sampling_rate
            )
            self.metrics_interpreter = MetricsInterpreter()
            
            # Initialize anti-ban system
            self.anti_ban_system = create_anti_ban_system()
            self.anti_ban_system.set_protection_level(self.config.protection_level)
            
            logging.info("✅ All components initialized successfully")
            
        except Exception as e:
            logging.error(f"❌ Component initialization failed: {e}")
            raise
    
    def start_session(self, session_name: str = None) -> bool:
        """Start enhanced recording session"""
        if self.is_recording:
            logging.warning("Session already active")
            return False
        
        try:
            # Generate session name if not provided
            if session_name is None:
                session_name = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            self.session_name = session_name
            self.session_start_time = time.time()
            self.session_data = {
                'session_name': session_name,
                'start_time': datetime.now().isoformat(),
                'config': self.config.__dict__,
                'data': {},
                'analysis': {},
                'security': {},
                'performance': {}
            }
            
            # Start data collection
            self.data_collector.start_recording()
            
            # Start anti-ban protection
            if self.config.enable_security:
                self.anti_ban_system.start_protection()
            
            # Start background analysis
            self._start_background_analysis()
            
            self.is_recording = True
            
            logging.info(f"📹 Enhanced session started: {session_name}")
            return True
            
        except Exception as e:
            logging.error(f"❌ Session start failed: {e}")
            return False
    
    def stop_session(self) -> Dict[str, Any]:
        """Stop session and perform comprehensive analysis"""
        if not self.is_recording:
            logging.warning("No active session to stop")
            return {}
        
        try:
            # Stop data collection
            self.data_collector.stop_recording()
            
            # Stop anti-ban protection
            if self.config.enable_security:
                self.anti_ban_system.stop_protection()
            
            # Stop background analysis
            self._stop_background_analysis()
            
            # Collect session data
            session_data = self.data_collector.stop_recording()
            self.session_data['data'] = session_data
            
            # Perform comprehensive analysis
            analysis_results = self._perform_comprehensive_analysis(session_data)
            self.session_data['analysis'] = analysis_results
            
            # Collect security data
            security_data = self.anti_ban_system.get_security_status()
            self.session_data['security'] = security_data
            
            # Collect performance data
            performance_data = self._collect_performance_stats()
            self.session_data['performance'] = performance_data
            
            # Save session data
            self._save_session_data()
            
            self.is_recording = False
            
            logging.info(f"📊 Session stopped and analyzed: {self.session_name}")
            return self.session_data
            
        except Exception as e:
            logging.error(f"❌ Session stop failed: {e}")
            return {}
    
    def _start_background_analysis(self):
        """Start background analysis tasks"""
        # Start async analysis loop
        self.async_loop = asyncio.new_event_loop()
        self.background_tasks.append(
            self.async_loop.create_task(self._background_analysis_loop())
        )
        
        # Start performance monitoring
        self.performance_monitor = threading.Thread(target=self._performance_monitor_loop)
        self.performance_monitor.daemon = True
        self.performance_monitor.start()
    
    def _stop_background_analysis(self):
        """Stop background analysis tasks"""
        if self.async_loop:
            self.async_loop.stop()
        
        if hasattr(self, 'performance_monitor'):
            self.performance_monitor.join(timeout=2.0)
    
    async def _background_analysis_loop(self):
        """Background analysis loop for real-time insights"""
        while self.is_recording:
            try:
                # Get current data
                current_data = self.data_collector.mouse_buffer.get_all()
                
                if len(current_data) > 100:  # Only analyze when we have enough data
                    # Real-time ML analysis
                    ml_results = self._analyze_with_ml(current_data)
                    
                    # Real-time security analysis
                    security_results = self._analyze_security(current_data)
                    
                    # Update session data
                    self.session_data['analysis']['real_time'] = {
                        'ml_results': ml_results,
                        'security_results': security_results,
                        'timestamp': time.time()
                    }
                
                # Sleep between analysis
                await asyncio.sleep(5.0)
                
            except Exception as e:
                logging.error(f"Background analysis error: {e}")
                await asyncio.sleep(1.0)
    
    def _performance_monitor_loop(self):
        """Monitor system performance during recording"""
        while self.is_recording:
            try:
                # Monitor memory usage
                import psutil
                memory_info = psutil.virtual_memory()
                self.performance_stats['memory_usage'] = memory_info.percent
                
                # Monitor processing time
                if hasattr(self.data_collector, '_processing_times'):
                    if self.data_collector._processing_times:
                        avg_time = np.mean(list(self.data_collector._processing_times))
                        self.performance_stats['processing_time'] = avg_time
                
                # Monitor security violations
                if self.anti_ban_system:
                    security_status = self.anti_ban_system.get_security_status()
                    self.performance_stats['security_violations'] = len(security_status.get('recent_events', []))
                
                # Sleep between monitoring
                time.sleep(10.0)
                
            except Exception as e:
                logging.error(f"Performance monitoring error: {e}")
                time.sleep(5.0)
    
    def _analyze_with_ml(self, mouse_data: List[Dict]) -> Dict[str, Any]:
        """Perform ML analysis on current data"""
        results = {}
        
        try:
            # Style classification
            if 'style_classifier' in self.ml_models:
                style, confidence = self.ml_models['style_classifier'].predict_with_confidence(mouse_data)
                results['style'] = {'prediction': style, 'confidence': confidence}
            
            # LSTM pattern analysis
            if 'lstm_trainer' in self.ml_models:
                pattern, confidence = self.ml_models['lstm_trainer'].predict_pattern(mouse_data)
                results['pattern'] = {'prediction': pattern, 'confidence': confidence}
            
            # Player clustering
            if 'player_clustering' in self.ml_models:
                # This would require more complex implementation
                results['clustering'] = {'status': 'pending_full_implementation'}
            
        except Exception as e:
            logging.error(f"ML analysis error: {e}")
            results['error'] = str(e)
        
        return results
    
    def _analyze_security(self, mouse_data: List[Dict]) -> Dict[str, Any]:
        """Perform security analysis on current data"""
        results = {}
        
        try:
            # Pattern analysis
            positions = [(d['x'], d['y']) for d in mouse_data if 'x' in d and 'y' in d]
            timestamps = [d['timestamp'] for d in mouse_data if 'timestamp' in d]
            
            if len(positions) > 10:
                pattern_analysis = self.anti_ban_system.analyze_movement_pattern(positions, timestamps)
                results['pattern_analysis'] = pattern_analysis
            
            # Security status
            security_status = self.anti_ban_system.get_security_status()
            results['security_status'] = security_status
            
        except Exception as e:
            logging.error(f"Security analysis error: {e}")
            results['error'] = str(e)
        
        return results
    
    def _perform_comprehensive_analysis(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive analysis on session data"""
        analysis = {}
        
        try:
            # Scientific metrics analysis
            mouse_data = session_data.get('mouse_data', [])
            if mouse_data:
                metrics = self.scientific_metrics.calculate_all_metrics(mouse_data)
                interpretation = self.metrics_interpreter.interpret_metrics(metrics)
                
                analysis['scientific_metrics'] = {
                    'metrics': metrics.__dict__,
                    'interpretation': interpretation
                }
                
                # Game-specific insights
                game_category = self._detect_game_category(mouse_data)
                insights = self.metrics_interpreter.get_game_specific_insights(metrics, game_category)
                analysis['game_insights'] = insights
            
            # ML analysis
            ml_analysis = self._analyze_session_with_ml(session_data)
            analysis['ml_analysis'] = ml_analysis
            
            # Performance analysis
            performance_analysis = self._analyze_performance(session_data)
            analysis['performance_analysis'] = performance_analysis
            
            # Security analysis
            security_analysis = self._analyze_session_security(session_data)
            analysis['security_analysis'] = security_analysis
            
        except Exception as e:
            logging.error(f"Comprehensive analysis error: {e}")
            analysis['error'] = str(e)
        
        return analysis
    
    def _analyze_session_with_ml(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze entire session with ML models"""
        results = {}
        
        try:
            mouse_data = session_data.get('mouse_data', [])
            
            if mouse_data:
                # Style analysis
                if 'style_classifier' in self.ml_models:
                    style, confidence = self.ml_models['style_classifier'].predict_with_confidence(mouse_data)
                    results['style'] = {
                        'prediction': style,
                        'confidence': confidence,
                        'description': self._get_style_description(style)
                    }
                
                # Pattern analysis
                if 'lstm_trainer' in self.ml_models:
                    pattern, confidence = self.ml_models['lstm_trainer'].predict_pattern(mouse_data)
                    results['pattern'] = {
                        'prediction': pattern,
                        'confidence': confidence,
                        'description': self._get_pattern_description(pattern)
                    }
                
                # Player profile
                player_profile = self._create_player_profile(mouse_data)
                results['player_profile'] = player_profile
            
        except Exception as e:
            logging.error(f"Session ML analysis error: {e}")
            results['error'] = str(e)
        
        return results
    
    def _analyze_performance(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze session performance"""
        results = {}
        
        try:
            # Data collection performance
            mouse_data = session_data.get('mouse_data', [])
            session_duration = session_data.get('session_duration', 0)
            
            if session_duration > 0:
                collection_rate = len(mouse_data) / session_duration
                results['collection_rate'] = collection_rate
            
            # Processing performance
            performance_stats = session_data.get('performance_stats', {})
            results['processing_time'] = performance_stats.get('processing_time', 0)
            results['memory_usage'] = performance_stats.get('memory_usage', 0)
            
            # Quality metrics
            results['data_quality'] = self._assess_data_quality(mouse_data)
            
        except Exception as e:
            logging.error(f"Performance analysis error: {e}")
            results['error'] = str(e)
        
        return results
    
    def _analyze_session_security(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze session security"""
        results = {}
        
        try:
            # Security violations
            security_stats = session_data.get('security_stats', {})
            results['security_violations'] = security_stats.get('anti_ban_violations', 0)
            
            # Security measures applied
            results['security_measures'] = {
                'jitter_applied': security_stats.get('jitter_applied', False),
                'encryption_enabled': security_stats.get('encryption_enabled', False)
            }
            
            # Threat assessment
            security_status = session_data.get('security', {})
            results['threat_assessment'] = security_status.get('system_state', {}).get('threat_level', 'UNKNOWN')
            
        except Exception as e:
            logging.error(f"Security analysis error: {e}")
            results['error'] = str(e)
        
        return results
    
    def _detect_game_category(self, mouse_data: List[Dict]) -> str:
        """Detect game category based on mouse movement patterns"""
        try:
            if len(mouse_data) < 50:
                return 'unknown'
            
            # Analyze movement characteristics
            speeds = []
            for i in range(1, min(100, len(mouse_data))):
                d1, d2 = mouse_data[i-1], mouse_data[i]
                if 'x' in d1 and 'y' in d1 and 'x' in d2 and 'y' in d2:
                    distance = ((d2['x'] - d1['x'])**2 + (d2['y'] - d1['y'])**2)**0.5
                    speeds.append(distance)
            
            if not speeds:
                return 'unknown'
            
            avg_speed = np.mean(speeds)
            speed_variance = np.var(speeds)
            
            # Game category detection logic
            if avg_speed > 50 and speed_variance > 1000:
                return 'tactical_fps'
            elif avg_speed > 30 and speed_variance > 500:
                return 'hero_fps'
            elif avg_speed < 20 and speed_variance < 100:
                return 'strategy'
            elif avg_speed > 20 and speed_variance > 200:
                return 'battle_royale'
            else:
                return 'survival'
                
        except Exception:
            return 'unknown'
    
    def _get_style_description(self, style: str) -> str:
        """Get description for player style"""
        descriptions = {
            'flicker': 'Aggressive player with quick, precise movements',
            'tracker': 'Smooth and consistent movement style',
            'micro_juster': 'Precise micro-adjustments with high accuracy',
            'hybrid': 'Mixed playstyle adapting to different situations'
        }
        return descriptions.get(style, 'Unknown playstyle')
    
    def _get_pattern_description(self, pattern: str) -> str:
        """Get description for movement pattern"""
        descriptions = {
            'flick': 'Quick directional changes and rapid movements',
            'tracking': 'Smooth tracking movements with consistent speed',
            'micro_adjustments': 'Small, precise adjustments to positioning',
            'burst': 'Short bursts of high-speed movement',
            'mixed': 'Complex combination of different movement types'
        }
        return descriptions.get(pattern, 'Unknown pattern')
    
    def _create_player_profile(self, mouse_data: List[Dict]) -> Dict[str, Any]:
        """Create comprehensive player profile"""
        profile = {
            'accuracy': 0.0,
            'consistency': 0.0,
            'reaction_time': 0.0,
            'movement_efficiency': 0.0,
            'complexity_score': 0.0
        }
        
        try:
            if len(mouse_data) < 20:
                return profile
            
            # Calculate accuracy (inverse of deviation from straight lines)
            positions = [(d['x'], d['y']) for d in mouse_data if 'x' in d and 'y' in d]
            if len(positions) >= 10:
                # Simplified accuracy calculation
                total_distance = 0
                direct_distance = 0
                
                for i in range(1, len(positions)):
                    total_distance += np.linalg.norm(np.array(positions[i]) - np.array(positions[i-1]))
                
                if len(positions) > 1:
                    direct_distance = np.linalg.norm(np.array(positions[-1]) - np.array(positions[0]))
                
                if total_distance > 0:
                    profile['accuracy'] = direct_distance / total_distance
            
            # Calculate consistency (inverse of speed variance)
            speeds = []
            for i in range(1, min(50, len(mouse_data))):
                d1, d2 = mouse_data[i-1], mouse_data[i]
                if 'x' in d1 and 'y' in d1 and 'x' in d2 and 'y' in d2:
                    distance = np.linalg.norm(np.array([d2['x'], d2['y']]) - np.array([d1['x'], d1['y']]))
                    speeds.append(distance)
            
            if speeds:
                speed_variance = np.var(speeds)
                profile['consistency'] = 1.0 / (1.0 + speed_variance)
            
            # Calculate complexity (based on direction changes)
            direction_changes = []
            for i in range(2, min(30, len(positions))):
                p1, p2, p3 = np.array(positions[i-2]), np.array(positions[i-1]), np.array(positions[i])
                v1, v2 = p2 - p1, p3 - p2
                
                if np.linalg.norm(v1) > 0 and np.linalg.norm(v2) > 0:
                    cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
                    cos_angle = np.clip(cos_angle, -1, 1)
                    angle = np.arccos(cos_angle)
                    direction_changes.append(angle)
            
            if direction_changes:
                profile['complexity_score'] = np.mean(direction_changes)
            
        except Exception as e:
            logging.error(f"Player profile creation error: {e}")
        
        return profile
    
    def _assess_data_quality(self, mouse_data: List[Dict]) -> Dict[str, Any]:
        """Assess the quality of collected data"""
        quality = {
            'completeness': 0.0,
            'consistency': 0.0,
            'accuracy': 0.0,
            'overall_score': 0.0
        }
        
        try:
            if not mouse_data:
                return quality
            
            # Completeness (ratio of valid data points)
            valid_points = sum(1 for d in mouse_data if 'x' in d and 'y' in d)
            quality['completeness'] = valid_points / len(mouse_data)
            
            # Consistency (temporal consistency)
            timestamps = [d['timestamp'] for d in mouse_data if 'timestamp' in d]
            if len(timestamps) > 1:
                intervals = np.diff(timestamps)
                interval_variance = np.var(intervals)
                quality['consistency'] = 1.0 / (1.0 + interval_variance * 1000)
            
            # Accuracy (spatial consistency)
            positions = [(d['x'], d['y']) for d in mouse_data if 'x' in d and 'y' in d]
            if len(positions) > 10:
                # Check for extreme outliers
                positions_array = np.array(positions)
                mean_pos = np.mean(positions_array, axis=0)
                std_pos = np.std(positions_array, axis=0)
                
                # Count outliers (beyond 3 standard deviations)
                outliers = 0
                for pos in positions_array:
                    if np.any(np.abs(pos - mean_pos) > 3 * std_pos):
                        outliers += 1
                
                quality['accuracy'] = 1.0 - (outliers / len(positions))
            
            # Overall score
            quality['overall_score'] = np.mean(list(quality.values())[:-1])  # Exclude overall_score
            
        except Exception as e:
            logging.error(f"Data quality assessment error: {e}")
        
        return quality
    
    def _collect_performance_stats(self) -> Dict[str, Any]:
        """Collect final performance statistics"""
        stats = self.performance_stats.copy()
        
        # Add session-specific stats
        if self.session_start_time:
            session_duration = time.time() - self.session_start_time
            stats['session_duration'] = session_duration
        
        return stats
    
    def _save_session_data(self):
        """Save session data to file"""
        try:
            # Create sessions directory
            sessions_dir = Path("sessions")
            sessions_dir.mkdir(exist_ok=True)
            
            # Generate filename
            filename = sessions_dir / f"{self.session_name}.json"
            
            # Save data
            with open(filename, 'w', encoding='utf-8') as f:
                # Convert dataclasses to dict for JSON serialization
                json_data = self._convert_to_serializable(self.session_data)
                json.dump(json_data, f, indent=2, ensure_ascii=False)
            
            logging.info(f"💾 Session data saved to: {filename}")
            
        except Exception as e:
            logging.error(f"Session data save failed: {e}")
    
    def _convert_to_serializable(self, obj):
        """Convert objects to JSON serializable format"""
        if isinstance(obj, dict):
            return {key: self._convert_to_serializable(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_to_serializable(item) for item in obj]
        elif hasattr(obj, '__dict__'):
            return self._convert_to_serializable(obj.__dict__)
        elif callable(obj):
            return f"<function {obj.__name__}>"
        elif hasattr(obj, '__class__') and obj.__class__.__name__ == 'dataclass':
            return self._convert_to_serializable(obj.__dict__)
        else:
            return obj
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get summary of current session"""
        if not self.is_recording:
            return {'status': 'not_recording'}
        
        summary = {
            'status': 'recording',
            'session_name': self.session_name,
            'duration': time.time() - self.session_start_time,
            'data_points': len(self.data_collector.mouse_buffer.get_all()),
            'performance': self.performance_stats,
            'security_status': self.anti_ban_system.get_security_status() if self.anti_ban_system else {}
        }
        
        return summary
    
    def export_session_report(self, format: str = 'json') -> str:
        """Export session report in specified format"""
        if not self.session_data:
            return "No session data to export"
        
        if format.lower() == 'json':
            return self._export_json_report()
        elif format.lower() == 'markdown':
            return self._export_markdown_report()
        else:
            return f"Unsupported format: {format}"
    
    def _export_json_report(self) -> str:
        """Export session report as JSON"""
        filename = f"report_{self.session_name}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json_data = self._convert_to_serializable(self.session_data)
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        
        return f"JSON report saved to: {filename}"
    
    def _export_markdown_report(self) -> str:
        """Export session report as Markdown"""
        filename = f"report_{self.session_name}.md"
        
        analysis = self.session_data.get('analysis', {})
        scientific_metrics = analysis.get('scientific_metrics', {})
        ml_analysis = analysis.get('ml_analysis', {})
        
        markdown_content = f"""# MouseAI Session Report

**Session:** {self.session_name}
**Date:** {self.session_data.get('start_time', 'Unknown')}
**Duration:** {self.session_data.get('session_duration', 0):.2f} seconds

## Scientific Metrics

"""
        
        if 'metrics' in scientific_metrics:
            metrics = scientific_metrics['metrics']
            for metric, value in metrics.items():
                markdown_content += f"- **{metric}:** {value}\n"
        
        markdown_content += "\n## ML Analysis\n\n"
        
        if 'style' in ml_analysis:
            style = ml_analysis['style']
            markdown_content += f"- **Play Style:** {style.get('prediction', 'Unknown')} (Confidence: {style.get('confidence', 0):.2f})\n"
            markdown_content += f"  - {style.get('description', '')}\n"
        
        if 'pattern' in ml_analysis:
            pattern = ml_analysis['pattern']
            markdown_content += f"- **Movement Pattern:** {pattern.get('prediction', 'Unknown')} (Confidence: {pattern.get('confidence', 0):.2f})\n"
            markdown_content += f"  - {pattern.get('description', '')}\n"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        return f"Markdown report saved to: {filename}"

def create_enhanced_mouseai(config: Optional[SessionConfig] = None) -> EnhancedMouseAI:
    """Factory for creating enhanced MouseAI system"""
    return EnhancedMouseAI(config)

# Example usage and testing
if __name__ == "__main__":
    print("🚀 Testing Enhanced MouseAI Integration...")
    
    # Create enhanced system
    config = SessionConfig(
        sampling_rate=100,
        enable_security=True,
        protection_level="MEDIUM"
    )
    
    mouseai = create_enhanced_mouseai(config)
    
    print("\n📊 System Status:")
    print(f"   Data Collector: {'✅' if mouseai.data_collector else '❌'}")
    print(f"   ML Models: {'✅' if mouseai.ml_models else '❌'}")
    print(f"   Scientific Metrics: {'✅' if mouseai.scientific_metrics else '❌'}")
    print(f"   Anti-Ban System: {'✅' if mouseai.anti_ban_system else '❌'}")
    
    # Test session
    print("\n📹 Starting test session...")
    success = mouseai.start_session("test_session")
    print(f"   Session started: {success}")
    
    if success:
        print("\n⏱️  Recording for 10 seconds...")
        time.sleep(10)
        
        print("\n📊 Session Summary:")
        summary = mouseai.get_session_summary()
        print(f"   Status: {summary['status']}")
        print(f"   Duration: {summary['duration']:.2f}s")
        print(f"   Data points: {summary['data_points']}")
        
        print("\n🛑 Stopping session...")
        session_data = mouseai.stop_session()
        
        if session_data:
            print("✅ Session completed successfully")
            
            # Export report
            print("\n📄 Exporting reports...")
            json_report = mouseai.export_session_report('json')
            markdown_report = mouseai.export_session_report('markdown')
            
            print(f"   {json_report}")
            print(f"   {markdown_report}")
        else:
            print("❌ Session completion failed")
    
    print("\n✅ Enhanced MouseAI integration test completed!")