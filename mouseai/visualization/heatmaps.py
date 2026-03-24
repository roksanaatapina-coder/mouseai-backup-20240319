#!/usr/bin/env python3
"""
Heatmaps - Тепловые карты движений и кликов
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple, Optional
import cv2
from pathlib import Path

class MouseHeatmap:
    """Генератор тепловых карт движений мыши"""
    
    def __init__(self, width=1920, height=1080, grid_size=50):
        self.width = width
        self.height = height
        self.grid_size = grid_size
        self.heatmap = None
        
    def generate_heatmap(self, mouse_data: List[Dict], 
                        normalize=True, blur_kernel=15) -> np.ndarray:
        """Сгенерировать тепловую карту из данных мыши"""
        
        # Создаем пустую карту
        heatmap = np.zeros((self.height, self.width))
        
        # Заполняем карту
        for data in mouse_data:
            if 'x' in data and 'y' in data:
                x, y = int(data['x']), int(data['y'])
                
                # Проверяем границы
                if 0 <= x < self.width and 0 <= y < self.height:
                    heatmap[y, x] += 1
                    
        # Сглаживание
        if blur_kernel > 0:
            heatmap = cv2.GaussianBlur(heatmap, (blur_kernel, blur_kernel), 0)
            
        # Нормализация
        if normalize and heatmap.max() > 0:
            heatmap = heatmap / heatmap.max()
            
        self.heatmap = heatmap
        return heatmap
        
    def save_heatmap(self, filepath: str, title="Mouse Movement Heatmap"):
        """Сохранить тепловую карту как изображение"""
        if self.heatmap is None:
            return False
            
        plt.figure(figsize=(16, 9), dpi=100)
        plt.imshow(self.heatmap, cmap='hot', interpolation='bilinear', alpha=0.8)
        plt.title(title, fontsize=16, fontweight='bold')
        plt.axis('off')
        plt.tight_layout()
        plt.savefig(filepath, dpi=100, bbox_inches='tight')
        plt.close()
        
        return True
        
    def overlay_heatmap(self, base_image: np.ndarray, alpha=0.6) -> np.ndarray:
        """Наложить тепловую карту на изображение"""
        if self.heatmap is None or base_image is None:
            return base_image
            
        # Преобразуем тепловую карту в цветное изображение
        heatmap_color = cv2.applyColorMap((self.heatmap * 255).astype(np.uint8), cv2.COLORMAP_HOT)
        
        # Накладываем с альфа-каналом
        result = cv2.addWeighted(base_image, 1-alpha, heatmap_color, alpha, 0)
        
        return result

class ClickHeatmap:
    """Генератор тепловых карт кликов"""
    
    def __init__(self, width=1920, height=1080, grid_size=50):
        self.width = width
        self.height = height
        self.grid_size = grid_size
        self.click_map = None
        self.pressure_map = None
        
    def generate_click_heatmap(self, mouse_data: List[Dict], 
                             click_type='both', normalize=True) -> np.ndarray:
        """Сгенерировать тепловую карту кликов"""
        
        click_map = np.zeros((self.height, self.width))
        
        for i, data in enumerate(mouse_data):
            if 'click' in data and data['click'] in ['left', 'right']:
                if click_type == 'both' or data['click'] == click_type:
                    x, y = int(data.get('x', 0)), int(data.get('y', 0))
                    
                    if 0 <= x < self.width and 0 <= y < self.height:
                        click_map[y, x] += 1
                        
        # Сглаживание
        click_map = cv2.GaussianBlur(click_map, (21, 21), 0)
        
        # Нормализация
        if normalize and click_map.max() > 0:
            click_map = click_map / click_map.max()
            
        self.click_map = click_map
        return click_map
        
    def generate_pressure_heatmap(self, mouse_data: List[Dict]) -> np.ndarray:
        """Сгенерировать карту "давления" (интенсивности кликов)"""
        pressure_map = np.zeros((self.height, self.width))
        
        for i, data in enumerate(mouse_data):
            if 'click' in data:
                x, y = int(data.get('x', 0)), int(data.get('y', 0))
                
                if 0 <= x < self.width and 0 <= y < self.height:
                    # Учитываем скорость перед кликом
                    if i > 0:
                        prev_data = mouse_data[i-1]
                        if 'x' in prev_data and 'y' in prev_data:
                            dx = data['x'] - prev_data['x']
                            dy = data['y'] - prev_data['y']
                            speed = (dx**2 + dy**2)**0.5
                            pressure_map[y, x] += speed * 0.1
                    else:
                        pressure_map[y, x] += 1.0
                        
        # Сглаживание
        pressure_map = cv2.GaussianBlur(pressure_map, (15, 15), 0)
        
        if pressure_map.max() > 0:
            pressure_map = pressure_map / pressure_map.max()
            
        self.pressure_map = pressure_map
        return pressure_map
        
    def create_combined_heatmap(self, mouse_data: List[Dict]) -> np.ndarray:
        """Создать комбинированную тепловую карту (движения + клики)"""
        
        # Генерируем карты
        movement_map = MouseHeatmap(self.width, self.height).generate_heatmap(mouse_data)
        click_map = self.generate_click_heatmap(mouse_data)
        
        # Комбинируем
        combined = np.zeros((self.height, self.width, 3))
        
        # Красный канал - клики
        combined[:, :, 0] = click_map * 255
        
        # Зеленый канал - движения
        combined[:, :, 1] = movement_map * 255
        
        # Синий канал - комбинация
        combined[:, :, 2] = (click_map + movement_map) / 2 * 255
        
        return combined.astype(np.uint8)

class TrajectoryVisualizer:
    """Визуализатор траекторий движений"""
    
    def __init__(self, width=1920, height=1080):
        self.width = width
        self.height = height
        
    def draw_trajectory(self, mouse_data: List[Dict], 
                       line_width=2, color=(255, 255, 255)) -> np.ndarray:
        """Нарисовать траекторию движений"""
        
        canvas = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        
        points = []
        for data in mouse_data:
            if 'x' in data and 'y' in data:
                x, y = int(data['x']), int(data['y'])
                if 0 <= x < self.width and 0 <= y < self.height:
                    points.append((x, y))
                    
        # Рисуем линии
        for i in range(1, len(points)):
            cv2.line(canvas, points[i-1], points[i], color, line_width)
            
        return canvas
        
    def draw_velocity_trajectory(self, mouse_data: List[Dict]) -> np.ndarray:
        """Нарисовать траекторию с кодированием скорости цветом"""
        
        canvas = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        
        if len(mouse_data) < 2:
            return canvas
            
        # Рассчитываем скорости
        velocities = []
        points = []
        
        for i in range(1, len(mouse_data)):
            prev_data = mouse_data[i-1]
            curr_data = mouse_data[i]
            
            if all(k in prev_data and k in curr_data for k in ['x', 'y']):
                dx = curr_data['x'] - prev_data['x']
                dy = curr_data['y'] - prev_data['y']
                speed = (dx**2 + dy**2)**0.5
                
                velocities.append(speed)
                points.append((int(curr_data['x']), int(curr_data['y'])))
                
        if not velocities:
            return canvas
            
        # Нормализуем скорости
        max_speed = max(velocities)
        if max_speed == 0:
            return canvas
            
        # Рисуем сегменты с разным цветом
        for i in range(1, len(points)):
            speed = velocities[i-1]
            normalized_speed = speed / max_speed
            
            # Цвет: синий (медленно) -> красный (быстро)
            color = (
                int(255 * (1 - normalized_speed)),  # Blue
                0,                                    # Green
                int(255 * normalized_speed)          # Red
            )
            
            cv2.line(canvas, points[i-1], points[i], color, 3)
            
        return canvas
        
    def create_speed_heatmap(self, mouse_data: List[Dict]) -> np.ndarray:
        """Создать карту скоростей"""
        
        speed_map = np.zeros((self.height, self.width))
        
        for i in range(1, len(mouse_data)):
            prev_data = mouse_data[i-1]
            curr_data = mouse_data[i]
            
            if all(k in prev_data and k in curr_data for k in ['x', 'y']):
                x, y = int(curr_data['x']), int(curr_data['y'])
                dx = curr_data['x'] - prev_data['x']
                dy = curr_data['y'] - prev_data['y']
                speed = (dx**2 + dy**2)**0.5
                
                if 0 <= x < self.width and 0 <= y < self.height:
                    speed_map[y, x] += speed
                    
        # Сглаживание
        speed_map = cv2.GaussianBlur(speed_map, (21, 21), 0)
        
        if speed_map.max() > 0:
            speed_map = speed_map / speed_map.max()
            
        return speed_map

class HeatmapGenerator:
    """Генератор всех типов тепловых карт"""
    
    def __init__(self, width=1920, height=1080):
        self.width = width
        self.height = height
        
    def generate_all_heatmaps(self, mouse_data: List[Dict], 
                             output_dir: str = "heatmaps") -> Dict[str, str]:
        """Сгенерировать все типы тепловых карт"""
        
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        results = {}
        
        # 1. Тепловая карта движений
        mouse_heatmap = MouseHeatmap(self.width, self.height)
        movement_map = mouse_heatmap.generate_heatmap(mouse_data)
        
        movement_file = output_path / "movement_heatmap.png"
        mouse_heatmap.save_heatmap(str(movement_file), "Mouse Movement Heatmap")
        results['movement'] = str(movement_file)
        
        # 2. Тепловая карта кликов
        click_heatmap = ClickHeatmap(self.width, self.height)
        click_map = click_heatmap.generate_click_heatmap(mouse_data)
        
        click_file = output_path / "click_heatmap.png"
        plt.figure(figsize=(16, 9), dpi=100)
        plt.imshow(click_map, cmap='viridis', interpolation='bilinear')
        plt.title("Click Heatmap", fontsize=16, fontweight='bold')
        plt.axis('off')
        plt.tight_layout()
        plt.savefig(str(click_file), dpi=100, bbox_inches='tight')
        plt.close()
        results['clicks'] = str(click_file)
        
        # 3. Комбинированная карта
        combined_map = click_heatmap.create_combined_heatmap(mouse_data)
        combined_file = output_path / "combined_heatmap.png"
        cv2.imwrite(str(combined_file), combined_map)
        results['combined'] = str(combined_file)
        
        # 4. Траектория
        trajectory_viz = TrajectoryVisualizer(self.width, self.height)
        trajectory = trajectory_viz.draw_trajectory(mouse_data)
        trajectory_file = output_path / "trajectory.png"
        cv2.imwrite(str(trajectory_file), trajectory)
        results['trajectory'] = str(trajectory_file)
        
        # 5. Траектория со скоростью
        velocity_trajectory = trajectory_viz.draw_velocity_trajectory(mouse_data)
        velocity_file = output_path / "velocity_trajectory.png"
        cv2.imwrite(str(velocity_file), velocity_trajectory)
        results['velocity_trajectory'] = str(velocity_file)
        
        # 6. Карта скоростей
        speed_map = trajectory_viz.create_speed_heatmap(mouse_data)
        speed_file = output_path / "speed_heatmap.png"
        plt.figure(figsize=(16, 9), dpi=100)
        plt.imshow(speed_map, cmap='plasma', interpolation='bilinear')
        plt.title("Speed Heatmap", fontsize=16, fontweight='bold')
        plt.axis('off')
        plt.tight_layout()
        plt.savefig(str(speed_file), dpi=100, bbox_inches='tight')
        plt.close()
        results['speed'] = str(speed_file)
        
        return results
        
    def create_comparison_heatmaps(self, data_sets: List[List[Dict]], 
                                  labels: List[str], output_file: str):
        """Создать сравнительные тепловые карты"""
        
        n_sets = len(data_sets)
        
        plt.figure(figsize=(20, 4*n_sets))
        
        for i, (data, label) in enumerate(zip(data_sets, labels)):
            plt.subplot(n_sets, 4, i*4 + 1)
            mouse_heatmap = MouseHeatmap(self.width, self.height)
            movement_map = mouse_heatmap.generate_heatmap(data)
            plt.imshow(movement_map, cmap='hot', interpolation='bilinear')
            plt.title(f"{label} - Movement")
            plt.axis('off')
            
            plt.subplot(n_sets, 4, i*4 + 2)
            click_heatmap = ClickHeatmap(self.width, self.height)
            click_map = click_heatmap.generate_click_heatmap(data)
            plt.imshow(click_map, cmap='viridis', interpolation='bilinear')
            plt.title(f"{label} - Clicks")
            plt.axis('off')
            
            plt.subplot(n_sets, 4, i*4 + 3)
            trajectory_viz = TrajectoryVisualizer(self.width, self.height)
            trajectory = trajectory_viz.draw_velocity_trajectory(data)
            plt.imshow(trajectory)
            plt.title(f"{label} - Velocity")
            plt.axis('off')
            
            plt.subplot(n_sets, 4, i*4 + 4)
            speed_map = trajectory_viz.create_speed_heatmap(data)
            plt.imshow(speed_map, cmap='plasma', interpolation='bilinear')
            plt.title(f"{label} - Speed")
            plt.axis('off')
            
        plt.tight_layout()
        plt.savefig(output_file, dpi=100, bbox_inches='tight')
        plt.close()

def create_heatmap_generator(width=1920, height=1080):
    """Фабрика для создания генератора тепловых карт"""
    return HeatmapGenerator(width, height)

# Пример использования
if __name__ == "__main__":
    print("🔥 Тестирование HeatmapGenerator...")
    
    # Создаем тестовые данные
    test_data = []
    for i in range(200):
        # Создаем спиральную траекторию
        angle = i * 0.1
        radius = i * 0.5
        x = 960 + radius * np.cos(angle) + np.random.normal(0, 10)
        y = 540 + radius * np.sin(angle) + np.random.normal(0, 10)
        
        # Добавляем случайные клики
        click = None
        if np.random.random() < 0.1:
            click = 'left' if np.random.random() < 0.7 else 'right'
            
        test_data.append({
            'x': x, 'y': y, 'click': click,
            'timestamp': i * 0.01
        })
        
    # Генерируем тепловые карты
    generator = create_heatmap_generator()
    results = generator.generate_all_heatmaps(test_data, "test_heatmaps")
    
    print("📊 Сгенерированные тепловые карты:")
    for name, filepath in results.items():
        print(f"   {name}: {filepath}")
        
    print("\n✅ Тепловые карты успешно созданы!")