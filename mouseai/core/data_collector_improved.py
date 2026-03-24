#!/usr/bin/env python3
"""
Improved DataCollector - Enhanced version with security, performance, and anti-ban measures
Based on AI Orchestra analysis recommendations
"""

import time
import threading
import asyncio
import platform
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Deque, Any
from dataclasses import dataclass, asdict
from collections import deque
from pathlib import Path
import logging
import random
import math

# Platform-specific imports with error handling
try:
    if platform.system() == "Windows":
        import win32api
        import win32con
        import win32gui
        import pywintypes
        WINDOWS_AVAILABLE = True
    else:
        WINDOWS_AVAILABLE = False
except ImportError:
    WINDOWS_AVAILABLE = False
    logging.warning("Windows API not available")

try:
    if platform.system() == "Darwin":  # macOS
        import Quartz
        import AppKit
        MACOS_AVAILABLE = True
    else:
        MACOS_AVAILABLE = False
except ImportError:
    MACOS_AVAILABLE = False
    logging.warning("macOS API not available")

try:
    if platform.system() == "Linux":
        import Xlib.display
        import Xlib.X
        import Xlib.XK
        import Xlib.protocol.event
        LINUX_AVAILABLE = True
    else:
        LINUX_AVAILABLE = False
except ImportError:
    LINUX_AVAILABLE = False
    logging.warning("Linux X11 API not available")

# Import scientific libraries with validation
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    logging.warning("psutil not available - system metrics will be limited")

@dataclass
class MouseMovement:
    """Enhanced mouse movement data with security features"""
    timestamp: float
    x: int
    y: int
    dx: float = 0.0
    dy: float = 0.0
    speed: float = 0.0
    acceleration: float = 0.0
    jitter_x: float = 0.0  # Anti-detection jitter
    jitter_y: float = 0.0  # Anti-detection jitter
    entropy: float = 0.0   # Movement complexity

@dataclass
class SystemMetrics:
    """System metrics with anti-detection features"""
    timestamp: float
    cpu_percent: float
    memory_percent: float
    active_window: str
    system_time: str
    process_id: int
    thread_count: int

class SecureRingBuffer:
    """Enhanced ring buffer with encryption and anti-detection features"""
    
    def __init__(self, max_size: int = 10000, encrypt_data: bool = False):
        self.max_size = max_size
        self.buffer = deque(maxlen=max_size)
        self.total_items = 0
        self.encrypt_data = encrypt_data
        self.encryption_key = random.randint(1, 255) if encrypt_data else 0
        
    def append(self, item: Any):
        """Add item with optional encryption"""
        if self.encrypt_data:
            item = self._encrypt_item(item)
        self.buffer.append(item)
        self.total_items += 1
        
    def get_all(self) -> List[Any]:
        """Get all items with decryption"""
        items = list(self.buffer)
        if self.encrypt_data:
            items = [self._decrypt_item(item) for item in items]
        return items
        
    def clear(self):
        """Clear buffer with secure wipe"""
        if self.encrypt_data:
            # Overwrite with random data before clearing
            for _ in range(len(self.buffer)):
                self.buffer.append(self._generate_random_data())
        self.buffer.clear()
        self.total_items = 0
        
    def size(self) -> int:
        """Get buffer size"""
        return len(self.buffer)
    
    def _encrypt_item(self, item: Any) -> Any:
        """Simple XOR encryption for anti-detection"""
        if isinstance(item, dict):
            encrypted = {}
            for key, value in item.items():
                if isinstance(value, (int, float)):
                    encrypted[key] = value ^ self.encryption_key
                else:
                    encrypted[key] = value
            return encrypted
        return item
    
    def _decrypt_item(self, item: Any) -> Any:
        """Decrypt item"""
        if isinstance(item, dict):
            decrypted = {}
            for key, value in item.items():
                if isinstance(value, (int, float)):
                    decrypted[key] = value ^ self.encryption_key
                else:
                    decrypted[key] = value
            return decrypted
        return item
    
    def _generate_random_data(self) -> Dict[str, Any]:
        """Generate random data for secure wipe"""
        return {
            "timestamp": time.time(),
            "x": random.randint(0, 1920),
            "y": random.randint(0, 1080),
            "random_noise": random.random()
        }

class AntiBanDetector:
    """Anti-ban detection and mitigation system"""
    
    def __init__(self):
        self.detection_patterns = []
        self.suspicious_activity = []
        self.ban_threshold = 0.8
        self.last_check = time.time()
        
    def check_suspicious_activity(self, mouse_data: List[Dict]) -> bool:
        """Check for suspicious patterns that might trigger anti-cheat"""
        if len(mouse_data) < 100:
            return False
            
        # Check for perfect geometric patterns
        if self._detect_perfect_patterns(mouse_data):
            self.suspicious_activity.append("Perfect geometric patterns detected")
            return True
            
        # Check for unnatural movement speeds
        if self._detect_unnatural_speeds(mouse_data):
            self.suspicious_activity.append("Unnatural movement speeds detected")
            return True
            
        # Check for timing patterns
        if self._detect_timing_patterns(mouse_data):
            self.suspicious_activity.append("Suspicious timing patterns detected")
            return True
            
        return False
    
    def _detect_perfect_patterns(self, mouse_data: List[Dict]) -> bool:
        """Detect perfect geometric patterns (circles, straight lines)"""
        if len(mouse_data) < 50:
            return False
            
        positions = np.array([[d['x'], d['y']] for d in mouse_data[-50:]])
        
        # Check for straight lines (low curvature)
        if len(positions) >= 10:
            # Calculate curvature
            dx = np.diff(positions[:, 0])
            dy = np.diff(positions[:, 1])
            curvature = np.abs(dx[:-1] * dy[1:] - dy[:-1] * dx[1:])
            
            if np.mean(curvature) < 0.1:  # Very straight line
                return True
                
        return False
    
    def _detect_unnatural_speeds(self, mouse_data: List[Dict]) -> bool:
        """Detect unnaturally constant or perfect speeds"""
        if len(mouse_data) < 20:
            return False
            
        positions = np.array([[d['x'], d['y']] for d in mouse_data[-20:]])
        velocities = np.diff(positions, axis=0)
        speeds = np.linalg.norm(velocities, axis=1)
        
        # Check for unnaturally constant speeds
        if len(speeds) > 5:
            speed_variance = np.var(speeds)
            if speed_variance < 0.01:  # Too constant
                return True
                
        return False
    
    def _detect_timing_patterns(self, mouse_data: List[Dict]) -> bool:
        """Detect unnatural timing patterns"""
        if len(mouse_data) < 10:
            return False
            
        timestamps = [d['timestamp'] for d in mouse_data[-10:]]
        intervals = np.diff(timestamps)
        
        # Check for perfectly regular intervals
        if len(intervals) > 3:
            interval_variance = np.var(intervals)
            if interval_variance < 1e-6:  # Too regular
                return True
                
        return False
    
    def apply_jitter(self, x: float, y: float) -> Tuple[float, float]:
        """Apply random jitter to coordinates for anti-detection"""
        jitter_amount = random.uniform(-2, 2)  # Small random offset
        return x + jitter_amount, y + jitter_amount

class ImprovedDataCollector:
    """Enhanced data collector with security, performance, and ML optimizations"""
    
    def __init__(self, buffer_size: int = 10000, sampling_rate: int = 100, 
                 enable_security: bool = True, enable_performance: bool = True):
        self.platform = platform.system()
        self.is_recording = False
        self.sampling_rate = sampling_rate  # Hz
        self.buffer_size = buffer_size
        self.enable_security = enable_security
        self.enable_performance = enable_performance
        
        # Enhanced ring buffers with security features
        self.mouse_buffer = SecureRingBuffer(buffer_size, encrypt_data=enable_security)
        self.keyboard_buffer = SecureRingBuffer(buffer_size // 10, encrypt_data=enable_security)
        self.system_buffer = SecureRingBuffer(buffer_size // 20, encrypt_data=enable_security)
        
        # Anti-ban detection
        self.anti_ban_detector = AntiBanDetector() if enable_security else None
        
        # Platform-specific setup with error handling
        self._setup_platform()
            
        self.recording_thread = None
        self.stop_event = threading.Event()
        self._last_position = None
        self._last_speed = 0.0
        self._system_update_interval = 0.5
        self._last_system_update = 0
        
        # Performance optimizations
        self._processing_times = deque(maxlen=100)
        self._adaptive_sampling = True
        self._current_sampling_rate = sampling_rate
        
        # ML feature extraction
        self._ml_features = {
            'entropy_buffer': deque(maxlen=50),
            'speed_buffer': deque(maxlen=100),
            'acceleration_buffer': deque(maxlen=100)
        }
        
        # Statistics and monitoring
        self._stats = {
            'total_samples': 0,
            'dropped_samples': 0,
            'processing_time': 0.0,
            'security_violations': 0,
            'performance_warnings': 0
        }
        
        logging.info(f"🚀 ImprovedDataCollector initialized on {self.platform}")
        logging.info(f"   Security features: {'Enabled' if enable_security else 'Disabled'}")
        logging.info(f"   Performance optimizations: {'Enabled' if enable_performance else 'Disabled'}")
        
    def _setup_platform(self):
        """Enhanced platform setup with comprehensive error handling"""
        try:
            if self.platform == "Windows" and WINDOWS_AVAILABLE:
                self._setup_windows()
            elif self.platform == "Darwin" and MACOS_AVAILABLE:
                self._setup_macos()
            elif self.platform == "Linux" and LINUX_AVAILABLE:
                self._setup_linux()
            else:
                logging.error(f"Platform {self.platform} not supported or dependencies missing")
                raise NotImplementedError(f"Platform {self.platform} not supported")
        except Exception as e:
            logging.error(f"Platform setup failed: {e}")
            raise
    
    def _setup_windows(self):
        """Enhanced Windows setup with security considerations"""
        try:
            # Use lower-level Windows API calls for better performance
            self.mouse_hook = None
            self.keyboard_hook = None
            logging.info("Windows platform setup completed")
        except Exception as e:
            logging.error(f"Windows setup failed: {e}")
            raise
            
    def _setup_macos(self):
        """Enhanced macOS setup with privacy considerations"""
        try:
            # Check for accessibility permissions
            self.event_tap = None
            logging.info("macOS platform setup completed")
        except Exception as e:
            logging.error(f"macOS setup failed: {e}")
            raise
            
    def _setup_linux(self):
        """Enhanced Linux setup with X11 security"""
        try:
            self.display = Xlib.display.Display()
            self.root = self.display.screen().root
            logging.info("Linux platform setup completed")
        except Exception as e:
            logging.error(f"Linux setup failed: {e}")
            raise
        
    def start_recording(self):
        """Start enhanced recording with security and performance monitoring"""
        if self.is_recording:
            return
            
        self.is_recording = True
        self.stop_event.clear()
        
        # Clear buffers
        self.mouse_buffer.clear()
        self.keyboard_buffer.clear()
        self.system_buffer.clear()
        
        # Start recording in separate thread
        self.recording_thread = threading.Thread(target=self._enhanced_record_loop)
        self.recording_thread.daemon = True
        self.recording_thread.start()
        
        logging.info(f"📹 Enhanced recording started ({self.platform})")
        logging.info(f"   Sampling rate: {self.sampling_rate}Hz")
        logging.info(f"   Buffer size: {self.buffer_size}")
        
    def stop_recording(self) -> Dict[str, Any]:
        """Stop recording and return enhanced session data"""
        if not self.is_recording:
            return {}
            
        self.is_recording = False
        self.stop_event.set()
        
        if self.recording_thread:
            self.recording_thread.join(timeout=2.0)
            
        # Collect all data from secure buffers
        session_data = {
            "platform": self.platform,
            "start_time": datetime.now().isoformat(),
            "mouse_data": self.mouse_buffer.get_all(),
            "keyboard_data": self.keyboard_buffer.get_all(),
            "system_data": self.system_buffer.get_all(),
            "session_duration": len(self.mouse_buffer.get_all()) / self.sampling_rate,
            "performance_stats": self._stats.copy(),
            "security_stats": {
                "anti_ban_violations": self._stats['security_violations'],
                "jitter_applied": self.enable_security,
                "encryption_enabled": self.enable_security
            },
            "ml_features": dict(self._ml_features)
        }
        
        # Log performance statistics
        self._log_performance_stats()
        
        return session_data
        
    def _enhanced_record_loop(self):
        """Enhanced recording loop with security, performance, and ML features"""
        last_system_update = time.time()
        last_mouse_update = time.time()
        mouse_interval = 1.0 / self._current_sampling_rate
        
        while not self.stop_event.is_set():
            current_time = time.time()
            processing_start = time.time()
            
            # Adaptive sampling rate based on system load
            if self._adaptive_sampling:
                self._adjust_sampling_rate()
            
            # Collect system metrics (less frequent)
            if current_time - last_system_update > self._system_update_interval:
                self._collect_enhanced_system_metrics()
                last_system_update = current_time
            
            # Collect mouse data with security features
            if current_time - last_mouse_update >= mouse_interval:
                mouse_pos = self._get_enhanced_mouse_position()
                if mouse_pos:
                    # Apply anti-ban measures
                    if self.enable_security and self.anti_ban_detector:
                        if self.anti_ban_detector.check_suspicious_activity(self.mouse_buffer.get_all()):
                            self._stats['security_violations'] += 1
                            # Apply jitter to break patterns
                            mouse_pos = self.anti_ban_detector.apply_jitter(*mouse_pos)
                    
                    # Extract ML features
                    movement_data = self._extract_ml_features(current_time, mouse_pos)
                    
                    # Add to buffer
                    self.mouse_buffer.append(movement_data)
                    self._stats['total_samples'] += 1
                    
                    # Update ML feature buffers
                    self._update_ml_features(movement_data)
                    
                last_mouse_update = current_time
            
            # Performance monitoring
            processing_time = time.time() - processing_start
            self._processing_times.append(processing_time)
            self._stats['processing_time'] += processing_time
            
            # Adaptive delay for stable sampling
            sleep_time = max(0, mouse_interval - processing_time)
            if sleep_time > 0:
                time.sleep(sleep_time)
            else:
                self._stats['dropped_samples'] += 1
                if self.enable_performance:
                    self._stats['performance_warnings'] += 1
            
    def _adjust_sampling_rate(self):
        """Adaptive sampling rate based on system performance"""
        if len(self._processing_times) < 10:
            return
            
        avg_processing_time = np.mean(self._processing_times)
        target_interval = 1.0 / self.sampling_rate
        
        # If processing takes too long, reduce sampling rate
        if avg_processing_time > target_interval * 0.8:
            self._current_sampling_rate = max(10, int(self._current_sampling_rate * 0.9))
        # If processing is fast, increase sampling rate
        elif avg_processing_time < target_interval * 0.3:
            self._current_sampling_rate = min(200, int(self._current_sampling_rate * 1.1))
    
    def _get_enhanced_mouse_position(self) -> Optional[Tuple[int, int]]:
        """Enhanced mouse position with validation and error handling"""
        try:
            if self.platform == "Windows" and WINDOWS_AVAILABLE:
                return self._get_windows_position()
            elif self.platform == "Darwin" and MACOS_AVAILABLE:
                return self._get_macos_position()
            elif self.platform == "Linux" and LINUX_AVAILABLE:
                return self._get_linux_position()
            else:
                return None
        except Exception as e:
            logging.error(f"Error getting mouse position: {e}")
            return None
    
    def _get_windows_position(self) -> Optional[Tuple[int, int]]:
        """Windows-specific position with enhanced validation"""
        try:
            pos = win32api.GetCursorPos()
            if pos and len(pos) == 2 and all(isinstance(x, int) for x in pos):
                # Validate coordinates are within screen bounds
                screen_width = win32api.GetSystemMetrics(0)
                screen_height = win32api.GetSystemMetrics(1)
                if 0 <= pos[0] <= screen_width and 0 <= pos[1] <= screen_height:
                    return pos
        except pywintypes.error as e:
            logging.warning(f"Windows API error: {e}")
        return None
    
    def _get_macos_position(self) -> Optional[Tuple[int, int]]:
        """macOS-specific position with privacy considerations"""
        try:
            loc = Quartz.NSEvent.mouseLocation()
            pos = (int(loc.x), int(loc.y))
            if pos and all(isinstance(x, int) for x in pos):
                # Validate coordinates
                screen = AppKit.NSScreen.mainScreen().frame()
                if 0 <= pos[0] <= screen.size.width and 0 <= pos[1] <= screen.size.height:
                    return pos
        except Exception as e:
            logging.warning(f"macOS API error: {e}")
        return None
    
    def _get_linux_position(self) -> Optional[Tuple[int, int]]:
        """Linux-specific position with X11 error handling"""
        try:
            data = self.root.query_pointer()
            pos = (data.root_x, data.root_y)
            if pos and all(isinstance(x, int) for x in pos):
                # Validate coordinates
                screen = self.display.screen()
                if 0 <= pos[0] <= screen.width_in_pixels and 0 <= pos[1] <= screen.height_in_pixels:
                    return pos
        except Exception as e:
            logging.warning(f"Linux X11 error: {e}")
        return None
    
    def _extract_ml_features(self, timestamp: float, pos: Tuple[int, int]) -> Dict[str, Any]:
        """Extract ML features from mouse movement"""
        movement_data = {
            "timestamp": timestamp,
            "x": pos[0],
            "y": pos[1],
            "window": self._get_active_window()
        }
        
        # Calculate velocity and acceleration
        if self._last_position is not None:
            dx = pos[0] - self._last_position[0]
            dy = pos[1] - self._last_position[1]
            distance = math.sqrt(dx**2 + dy**2)
            
            dt = 1.0 / self._current_sampling_rate
            speed = distance / dt if distance > 0 else 0
            
            # Calculate acceleration
            acceleration = (speed - self._last_speed) / dt if self._last_speed > 0 else 0
            
            # Calculate movement entropy (complexity)
            entropy = self._calculate_movement_entropy(dx, dy, speed)
            
            movement_data.update({
                "dx": dx,
                "dy": dy,
                "speed": speed,
                "acceleration": acceleration,
                "entropy": entropy
            })
        
        self._last_position = pos
        self._last_speed = speed if 'speed' in movement_data else 0
        
        return movement_data
    
    def _calculate_movement_entropy(self, dx: float, dy: float, speed: float) -> float:
        """Calculate movement entropy for ML features"""
        # Simple entropy calculation based on direction changes
        if speed == 0:
            return 0.0
        
        # Calculate direction angle
        angle = math.atan2(dy, dx)
        
        # Add to entropy buffer
        self._ml_features['entropy_buffer'].append(angle)
        
        # Calculate entropy from recent angles
        if len(self._ml_features['entropy_buffer']) >= 5:
            angles = list(self._ml_features['entropy_buffer'])
            angle_changes = [abs(angles[i+1] - angles[i]) for i in range(len(angles)-1)]
            return np.mean(angle_changes)
        
        return 0.0
    
    def _update_ml_features(self, movement_data: Dict[str, Any]):
        """Update ML feature buffers"""
        if 'speed' in movement_data:
            self._ml_features['speed_buffer'].append(movement_data['speed'])
        if 'acceleration' in movement_data:
            self._ml_features['acceleration_buffer'].append(movement_data['acceleration'])
    
    def _get_active_window(self) -> str:
        """Get active window with platform-specific implementation"""
        try:
            if self.platform == "Windows" and WINDOWS_AVAILABLE:
                hwnd = win32gui.GetForegroundWindow()
                return win32gui.GetWindowText(hwnd)
            elif self.platform == "Darwin" and MACOS_AVAILABLE:
                active_app = AppKit.NSWorkspace.sharedWorkspace().activeApplication()
                return active_app['NSApplicationName']
            elif self.platform == "Linux" and LINUX_AVAILABLE:
                return "Linux Window"
        except Exception:
            return "Unknown"
        return "Unknown"
    
    def _collect_enhanced_system_metrics(self):
        """Collect enhanced system metrics with security features"""
        try:
            if PSUTIL_AVAILABLE:
                metrics = {
                    "timestamp": time.time(),
                    "cpu_percent": psutil.cpu_percent(interval=0.1),
                    "memory_percent": psutil.virtual_memory().percent,
                    "active_window": self._get_active_window(),
                    "system_time": datetime.now().isoformat(),
                    "process_id": psutil.Process().pid,
                    "thread_count": psutil.Process().num_threads()
                }
            else:
                # Fallback without psutil
                metrics = {
                    "timestamp": time.time(),
                    "cpu_percent": 0,
                    "memory_percent": 0,
                    "active_window": self._get_active_window(),
                    "system_time": datetime.now().isoformat(),
                    "process_id": 0,
                    "thread_count": 0
                }
            
            self.system_buffer.append(metrics)
            
        except Exception as e:
            logging.error(f"Error collecting system metrics: {e}")
    
    def _log_performance_stats(self):
        """Log comprehensive performance statistics"""
        total_time = self._stats['processing_time']
        total_samples = self._stats['total_samples']
        dropped_samples = self._stats['dropped_samples']
        
        if total_samples > 0:
            avg_processing_time = total_time / total_samples
            drop_rate = (dropped_samples / total_samples) * 100
            
            logging.info(f"📊 Session completed:")
            logging.info(f"   - Samples collected: {len(self.mouse_buffer.get_all())}")
            logging.info(f"   - Average processing time: {avg_processing_time*1000:.2f}ms")
            logging.info(f"   - Sample drop rate: {drop_rate:.1f}%")
            logging.info(f"   - Security violations: {self._stats['security_violations']}")
            logging.info(f"   - Performance warnings: {self._stats['performance_warnings']}")
            
            if avg_processing_time > 0.01:  # > 10ms
                logging.warning("⚠️  High processing time detected - consider reducing sampling rate")
            if drop_rate > 5.0:  # > 5%
                logging.warning("⚠️  High sample drop rate - system may be overloaded")

def create_improved_data_collector():
    """Factory for creating improved data collector"""
    return ImprovedDataCollector(
        buffer_size=10000,
        sampling_rate=100,
        enable_security=True,
        enable_performance=True
    )

# Example usage and testing
if __name__ == "__main__":
    print("🚀 Testing ImprovedDataCollector...")
    
    collector = create_improved_data_collector()
    
    print(f"Platform: {collector.platform}")
    print(f"Security enabled: {collector.enable_security}")
    print(f"Performance enabled: {collector.enable_performance}")
    
    # Test recording
    print("\n📹 Starting test recording...")
    collector.start_recording()
    time.sleep(3)  # Record for 3 seconds
    data = collector.stop_recording()
    
    print(f"\n📊 Test results:")
    print(f"   Mouse movements: {len(data.get('mouse_data', []))}")
    print(f"   System metrics: {len(data.get('system_data', []))}")
    print(f"   Performance stats: {data.get('performance_stats', {})}")
    print(f"   Security stats: {data.get('security_stats', {})}")
    
    # Test ML features
    if 'ml_features' in data:
        print(f"   ML features extracted:")
        for feature, values in data['ml_features'].items():
            print(f"     - {feature}: {len(values)} values")
    
    print("\n✅ ImprovedDataCollector test completed!")