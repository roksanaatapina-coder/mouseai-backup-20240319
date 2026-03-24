#!/usr/bin/env python3
"""
Anti-Ban System - Comprehensive security and anti-detection system for MouseAI
Based on AI Orchestra analysis recommendations for anti-cheat evasion
"""

import time
import random
import threading
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
import logging
import hashlib
import os
import psutil
from datetime import datetime, timedelta

@dataclass
class SecurityEvent:
    """Security event with detailed information"""
    timestamp: float
    event_type: str
    severity: str  # 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'
    description: str
    data: Dict[str, Any]
    action_taken: str

class BehavioralRandomizer:
    """Randomizes mouse behavior to avoid detection patterns"""
    
    def __init__(self):
        self.jitter_strength = 0.5  # Base jitter strength
        self.timing_variance = 0.1  # Timing variation
        self.pattern_disruptor = 0.1  # Pattern disruption frequency
        
    def apply_jitter(self, x: float, y: float, intensity: float = None) -> Tuple[float, float]:
        """Apply random jitter to coordinates"""
        if intensity is None:
            intensity = self.jitter_strength
            
        jitter_x = random.uniform(-intensity, intensity)
        jitter_y = random.uniform(-intensity, intensity)
        
        return x + jitter_x, y + jitter_y
    
    def randomize_timing(self, base_delay: float) -> float:
        """Randomize timing delays"""
        variance = random.uniform(-self.timing_variance, self.timing_variance)
        return max(0.001, base_delay + (base_delay * variance))
    
    def disrupt_pattern(self, sequence: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
        """Disrupt repetitive movement patterns"""
        if len(sequence) < 5:
            return sequence
            
        # Add random micro-pauses
        if random.random() < self.pattern_disruptor:
            # Insert random pause
            pause_index = random.randint(1, len(sequence) - 1)
            pause_duration = random.uniform(0.01, 0.05)
            sequence.insert(pause_index, (sequence[pause_index][0], sequence[pause_index][1]))
        
        # Add random direction changes
        if random.random() < self.pattern_disruptor * 0.5:
            # Slight direction change
            change_index = random.randint(1, len(sequence) - 1)
            angle_change = random.uniform(-0.1, 0.1)
            x, y = sequence[change_index]
            sequence[change_index] = (x + angle_change, y + angle_change)
            
        return sequence

class PatternDetector:
    """Detects and prevents suspicious movement patterns"""
    
    def __init__(self):
        self.window_size = 50
        self.pattern_history = []
        self.suspicious_thresholds = {
            'straight_line': 0.1,      # Maximum curvature for straight line detection
            'perfect_circle': 0.05,     # Maximum deviation for circle detection
            'timing_regular': 1e-6,     # Maximum timing variance for regularity detection
            'speed_constant': 0.01      # Maximum speed variance for constant speed detection
        }
    
    def analyze_movement(self, positions: List[Tuple[float, float]], 
                        timestamps: List[float]) -> Dict[str, Any]:
        """Analyze movement for suspicious patterns"""
        if len(positions) < 10:
            return {'suspicious': False, 'patterns': [], 'score': 0.0}
        
        # Analyze straight line patterns
        straight_score = self._detect_straight_lines(positions)
        
        # Analyze circular patterns
        circle_score = self._detect_circular_patterns(positions)
        
        # Analyze timing patterns
        timing_score = self._detect_timing_patterns(timestamps)
        
        # Analyze speed patterns
        speed_score = self._detect_speed_patterns(positions, timestamps)
        
        # Calculate overall suspicious score
        total_score = (straight_score + circle_score + timing_score + speed_score) / 4.0
        
        # Determine if suspicious
        is_suspicious = total_score > 0.5
        
        patterns = []
        if straight_score > self.suspicious_thresholds['straight_line']:
            patterns.append('straight_line')
        if circle_score > self.suspicious_thresholds['perfect_circle']:
            patterns.append('perfect_circle')
        if timing_score > self.suspicious_thresholds['timing_regular']:
            patterns.append('timing_regular')
        if speed_score > self.suspicious_thresholds['speed_constant']:
            patterns.append('speed_constant')
        
        return {
            'suspicious': is_suspicious,
            'patterns': patterns,
            'score': total_score,
            'details': {
                'straight_line_score': straight_score,
                'circle_score': circle_score,
                'timing_score': timing_score,
                'speed_score': speed_score
            }
        }
    
    def _detect_straight_lines(self, positions: List[Tuple[float, float]]) -> float:
        """Detect straight line movements"""
        if len(positions) < 10:
            return 0.0
        
        # Calculate curvature
        curvatures = []
        for i in range(1, len(positions) - 1):
            p1, p2, p3 = np.array(positions[i-1]), np.array(positions[i]), np.array(positions[i+1])
            
            # Calculate angle
            v1 = p2 - p1
            v2 = p3 - p2
            
            if np.linalg.norm(v1) == 0 or np.linalg.norm(v2) == 0:
                continue
                
            cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
            cos_angle = np.clip(cos_angle, -1, 1)
            angle = np.arccos(cos_angle)
            
            curvatures.append(angle)
        
        if not curvatures:
            return 0.0
        
        # Calculate straightness score (low curvature = straight line)
        mean_curvature = np.mean(curvatures)
        return 1.0 - min(mean_curvature / 0.1, 1.0)
    
    def _detect_circular_patterns(self, positions: List[Tuple[float, float]]) -> float:
        """Detect perfect circular movements"""
        if len(positions) < 20:
            return 0.0
        
        # Try to fit a circle to the points
        positions_array = np.array(positions)
        
        # Calculate centroid
        centroid = np.mean(positions_array, axis=0)
        
        # Calculate distances from centroid
        distances = np.linalg.norm(positions_array - centroid, axis=1)
        
        # Check if distances are consistent (perfect circle)
        distance_variance = np.var(distances)
        mean_distance = np.mean(distances)
        
        if mean_distance == 0:
            return 0.0
        
        # Circle score (low variance = perfect circle)
        circle_score = 1.0 - min(distance_variance / (mean_distance * 0.1), 1.0)
        
        return circle_score
    
    def _detect_timing_patterns(self, timestamps: List[float]) -> float:
        """Detect regular timing patterns"""
        if len(timestamps) < 10:
            return 0.0
        
        # Calculate intervals
        intervals = np.diff(timestamps)
        
        if len(intervals) < 5:
            return 0.0
        
        # Check for regular intervals
        interval_variance = np.var(intervals)
        
        # Regular timing score (low variance = regular timing)
        return 1.0 - min(interval_variance / 1e-6, 1.0)
    
    def _detect_speed_patterns(self, positions: List[Tuple[float, float]], 
                              timestamps: List[float]) -> float:
        """Detect constant speed patterns"""
        if len(positions) < 10 or len(timestamps) < 10:
            return 0.0
        
        # Calculate speeds
        speeds = []
        for i in range(1, len(positions)):
            distance = np.linalg.norm(np.array(positions[i]) - np.array(positions[i-1]))
            time_diff = timestamps[i] - timestamps[i-1]
            
            if time_diff > 0:
                speed = distance / time_diff
                speeds.append(speed)
        
        if len(speeds) < 5:
            return 0.0
        
        # Check for constant speed
        speed_variance = np.var(speeds)
        mean_speed = np.mean(speeds)
        
        if mean_speed == 0:
            return 0.0
        
        # Constant speed score (low variance = constant speed)
        return 1.0 - min(speed_variance / (mean_speed * 0.1), 1.0)

class SystemMonitor:
    """Monitors system state for security threats"""
    
    def __init__(self):
        self.process_whitelist = self._get_process_whitelist()
        self.security_processes = self._get_security_processes()
        self.last_check = time.time()
        
    def _get_process_whitelist(self) -> List[str]:
        """Get list of trusted processes"""
        return [
            'explorer.exe', 'chrome.exe', 'firefox.exe', 'steam.exe',
            'gameoverlayui.exe', 'origin.exe', 'uplay.exe', 'eaapp.exe'
        ]
    
    def _get_security_processes(self) -> List[str]:
        """Get list of security/anti-cheat processes to monitor"""
        return [
            'easyanticheat.exe', 'battleye.exe', 'vac.exe', 'faceit.exe',
            'aimlabs.exe', 'walao.exe', 'cheatengine.exe'
        ]
    
    def check_system_state(self) -> Dict[str, Any]:
        """Check current system state for security threats"""
        current_time = time.time()
        
        if current_time - self.last_check < 1.0:  # Check every second
            return {'status': 'cached'}
        
        self.last_check = current_time
        
        # Get running processes
        running_processes = []
        suspicious_processes = []
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'exe']):
                try:
                    process_info = proc.info
                    running_processes.append(process_info['name'].lower())
                    
                    # Check for suspicious processes
                    if process_info['name'].lower() in self.security_processes:
                        suspicious_processes.append(process_info['name'])
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        
        except Exception as e:
            logging.warning(f"Process monitoring failed: {e}")
        
        # Check system resources
        cpu_usage = psutil.cpu_percent(interval=0.1)
        memory_info = psutil.virtual_memory()
        
        # Check for debugging tools
        debugger_detected = self._check_debuggers()
        
        return {
            'timestamp': current_time,
            'running_processes': running_processes,
            'suspicious_processes': suspicious_processes,
            'cpu_usage': cpu_usage,
            'memory_usage': memory_info.percent,
            'debugger_detected': debugger_detected,
            'threat_level': self._calculate_threat_level(suspicious_processes, cpu_usage, debugger_detected)
        }
    
    def _check_debuggers(self) -> bool:
        """Check for debugger presence"""
        try:
            # Check for common debugger indicators
            import ctypes
            
            # Check if being debugged
            is_debugger_present = ctypes.windll.kernel32.IsDebuggerPresent()
            if is_debugger_present:
                return True
                
            # Check for common debugger processes
            debugger_names = ['ollydbg.exe', 'x64dbg.exe', 'ida.exe', 'windbg.exe']
            for proc in psutil.process_iter(['name']):
                if proc.info['name'].lower() in debugger_names:
                    return True
                    
        except Exception:
            pass
        
        return False
    
    def _calculate_threat_level(self, suspicious_processes: List[str], 
                               cpu_usage: float, debugger_detected: bool) -> str:
        """Calculate overall threat level"""
        threat_score = 0
        
        # Suspicious processes
        threat_score += len(suspicious_processes) * 25
        
        # High CPU usage
        if cpu_usage > 80:
            threat_score += 20
        
        # Debugger detected
        if debugger_detected:
            threat_score += 50
        
        # Determine threat level
        if threat_score >= 75:
            return 'CRITICAL'
        elif threat_score >= 50:
            return 'HIGH'
        elif threat_score >= 25:
            return 'MEDIUM'
        else:
            return 'LOW'

class AntiBanSystem:
    """Main anti-ban system coordinator"""
    
    def __init__(self):
        self.behavioral_randomizer = BehavioralRandomizer()
        self.pattern_detector = PatternDetector()
        self.system_monitor = SystemMonitor()
        
        self.is_active = False
        self.security_events = []
        self.protection_level = 'MEDIUM'  # LOW, MEDIUM, HIGH, MAXIMUM
        
        # Configuration
        self.config = {
            'jitter_enabled': True,
            'pattern_detection_enabled': True,
            'system_monitoring_enabled': True,
            'auto_protection_enabled': True,
            'logging_enabled': True
        }
        
        self.monitoring_thread = None
        self.stop_monitoring = threading.Event()
        
        logging.info("🛡️ Anti-Ban System initialized")
    
    def start_protection(self):
        """Start anti-ban protection"""
        if self.is_active:
            return
        
        self.is_active = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
        
        logging.info("🛡️ Anti-Ban protection started")
    
    def stop_protection(self):
        """Stop anti-ban protection"""
        if not self.is_active:
            return
        
        self.is_active = False
        self.stop_monitoring.set()
        
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=2.0)
        
        logging.info("🛡️ Anti-Ban protection stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while not self.stop_monitoring.is_set():
            try:
                # System monitoring
                if self.config['system_monitoring_enabled']:
                    system_state = self.system_monitor.check_system_state()
                    self._handle_system_state(system_state)
                
                # Sleep between checks
                time.sleep(1.0)
                
            except Exception as e:
                logging.error(f"Monitoring loop error: {e}")
                time.sleep(1.0)
    
    def _handle_system_state(self, system_state: Dict[str, Any]):
        """Handle system state changes"""
        if system_state.get('threat_level') == 'CRITICAL':
            self._trigger_emergency_protection(system_state)
        elif system_state.get('threat_level') == 'HIGH':
            self._trigger_high_protection(system_state)
        elif system_state.get('threat_level') == 'MEDIUM':
            self._trigger_medium_protection(system_state)
    
    def _trigger_emergency_protection(self, system_state: Dict[str, Any]):
        """Trigger emergency protection measures"""
        self._log_security_event(
            'EMERGENCY_PROTECTION',
            'CRITICAL',
            f"Critical threat detected: {system_state.get('suspicious_processes', [])}",
            system_state
        )
        
        # Maximum jitter
        self.behavioral_randomizer.jitter_strength = 2.0
        self.behavioral_randomizer.pattern_disruptor = 0.5
        
        # Log warning
        logging.critical("🚨 EMERGENCY PROTECTION ACTIVATED")
    
    def _trigger_high_protection(self, system_state: Dict[str, Any]):
        """Trigger high protection measures"""
        self._log_security_event(
            'HIGH_PROTECTION',
            'HIGH',
            f"High threat detected: {system_state.get('suspicious_processes', [])}",
            system_state
        )
        
        # High jitter
        self.behavioral_randomizer.jitter_strength = 1.0
        self.behavioral_randomizer.pattern_disruptor = 0.3
    
    def _trigger_medium_protection(self, system_state: Dict[str, Any]):
        """Trigger medium protection measures"""
        self._log_security_event(
            'MEDIUM_PROTECTION',
            'MEDIUM',
            f"Medium threat detected: {system_state.get('suspicious_processes', [])}",
            system_state
        )
        
        # Medium jitter
        self.behavioral_randomizer.jitter_strength = 0.5
        self.behavioral_randomizer.pattern_disruptor = 0.1
    
    def analyze_movement_pattern(self, positions: List[Tuple[float, float]], 
                                timestamps: List[float]) -> Dict[str, Any]:
        """Analyze movement pattern for suspicious behavior"""
        if not self.config['pattern_detection_enabled']:
            return {'suspicious': False, 'action': 'none'}
        
        analysis = self.pattern_detector.analyze_movement(positions, timestamps)
        
        if analysis['suspicious']:
            self._log_security_event(
                'SUSPICIOUS_PATTERN',
                'HIGH',
                f"Suspicious movement pattern detected: {analysis['patterns']}",
                analysis
            )
            
            # Apply pattern disruption
            disrupted_positions = self.behavioral_randomizer.disrupt_pattern(positions)
            
            return {
                'suspicious': True,
                'patterns': analysis['patterns'],
                'score': analysis['score'],
                'action': 'pattern_disrupted',
                'disrupted_positions': disrupted_positions
            }
        
        return {'suspicious': False, 'action': 'none'}
    
    def apply_behavioral_randomization(self, x: float, y: float, 
                                     base_delay: float = 0.01) -> Tuple[float, float, float]:
        """Apply behavioral randomization to coordinates and timing"""
        if not self.config['jitter_enabled']:
            return x, y, base_delay
        
        # Apply jitter
        jittered_x, jittered_y = self.behavioral_randomizer.apply_jitter(x, y)
        
        # Randomize timing
        randomized_delay = self.behavioral_randomizer.randomize_timing(base_delay)
        
        return jittered_x, jittered_y, randomized_delay
    
    def _log_security_event(self, event_type: str, severity: str, 
                           description: str, data: Dict[str, Any]):
        """Log security event"""
        if not self.config['logging_enabled']:
            return
        
        event = SecurityEvent(
            timestamp=time.time(),
            event_type=event_type,
            severity=severity,
            description=description,
            data=data,
            action_taken="auto_protection_applied"
        )
        
        self.security_events.append(event)
        
        # Keep only last 1000 events
        if len(self.security_events) > 1000:
            self.security_events.pop(0)
        
        # Log to file
        logging.warning(f"🛡️ Security Event: {event_type} - {severity} - {description}")
    
    def get_security_status(self) -> Dict[str, Any]:
        """Get current security status"""
        system_state = self.system_monitor.check_system_state()
        
        return {
            'active': self.is_active,
            'protection_level': self.protection_level,
            'config': self.config,
            'system_state': system_state,
            'recent_events': [e.__dict__ for e in self.security_events[-10:]],
            'jitter_strength': self.behavioral_randomizer.jitter_strength,
            'pattern_disruptor': self.behavioral_randomizer.pattern_disruptor
        }
    
    def set_protection_level(self, level: str):
        """Set protection level"""
        if level in ['LOW', 'MEDIUM', 'HIGH', 'MAXIMUM']:
            self.protection_level = level
            
            if level == 'LOW':
                self.behavioral_randomizer.jitter_strength = 0.1
                self.behavioral_randomizer.pattern_disruptor = 0.05
            elif level == 'MEDIUM':
                self.behavioral_randomizer.jitter_strength = 0.5
                self.behavioral_randomizer.pattern_disruptor = 0.1
            elif level == 'HIGH':
                self.behavioral_randomizer.jitter_strength = 1.0
                self.behavioral_randomizer.pattern_disruptor = 0.3
            elif level == 'MAXIMUM':
                self.behavioral_randomizer.jitter_strength = 2.0
                self.behavioral_randomizer.pattern_disruptor = 0.5
            
            logging.info(f"🛡️ Protection level set to: {level}")
    
    def export_security_report(self, filepath: str = None) -> str:
        """Export security report"""
        if filepath is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"security_report_{timestamp}.txt"
        
        status = self.get_security_status()
        
        report = f"""
MouseAI Security Report
Generated: {datetime.now().isoformat()}
========================================

Protection Status:
- Active: {status['active']}
- Protection Level: {status['protection_level']}
- Jitter Strength: {status['jitter_strength']}
- Pattern Disruptor: {status['pattern_disruptor']}

System State:
- Threat Level: {status['system_state']['threat_level']}
- CPU Usage: {status['system_state']['cpu_usage']:.1f}%
- Memory Usage: {status['system_state']['memory_usage']:.1f}%
- Suspicious Processes: {', '.join(status['system_state']['suspicious_processes'])}

Recent Security Events:
"""
        
        for event in status['recent_events']:
            report += f"- {event['event_type']}: {event['severity']} - {event['description']}\n"
        
        report += f"\nConfiguration:\n"
        for key, value in status['config'].items():
            report += f"- {key}: {value}\n"
        
        with open(filepath, 'w') as f:
            f.write(report)
        
        logging.info(f"🛡️ Security report exported to: {filepath}")
        return filepath

def create_anti_ban_system():
    """Factory for creating anti-ban system"""
    return AntiBanSystem()

# Example usage
if __name__ == "__main__":
    print("🛡️ Testing Anti-Ban System...")
    
    anti_ban = create_anti_ban_system()
    
    # Start protection
    anti_ban.start_protection()
    
    # Test behavioral randomization
    print("\n🎯 Testing Behavioral Randomization:")
    original_x, original_y = 100.0, 200.0
    jittered_x, jittered_y, delay = anti_ban.apply_behavioral_randomization(original_x, original_y, 0.01)
    print(f"   Original: ({original_x}, {original_y}) -> Jittered: ({jittered_x:.2f}, {jittered_y:.2f})")
    print(f"   Delay: {delay:.4f}s")
    
    # Test pattern detection
    print("\n🔍 Testing Pattern Detection:")
    # Create artificial straight line pattern
    positions = [(i, i) for i in range(100)]
    timestamps = [i * 0.01 for i in range(100)]
    
    analysis = anti_ban.analyze_movement_pattern(positions, timestamps)
    print(f"   Suspicious: {analysis['suspicious']}")
    if analysis['suspicious']:
        print(f"   Patterns: {analysis['patterns']}")
        print(f"   Score: {analysis['score']:.3f}")
    
    # Test security status
    print("\n📊 Security Status:")
    status = anti_ban.get_security_status()
    print(f"   Active: {status['active']}")
    print(f"   Threat Level: {status['system_state']['threat_level']}")
    print(f"   CPU Usage: {status['system_state']['cpu_usage']:.1f}%")
    
    # Export report
    print("\n📄 Exporting Security Report...")
    report_path = anti_ban.export_security_report()
    print(f"   Report saved to: {report_path}")
    
    # Stop protection
    anti_ban.stop_protection()
    
    print("\n✅ Anti-Ban System test completed!")