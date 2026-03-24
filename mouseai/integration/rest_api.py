#!/usr/bin/env python3
"""
REST API Integration - REST API для интеграции с внешними сервисами
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from typing import Dict, List, Optional
from datetime import datetime
import json

class RESTAPI:
    """REST API для MouseAI"""
    
    def __init__(self, mouseai_instance=None, host='localhost', port=5000):
        self.app = Flask(__name__)
        CORS(self.app)
        
        self.mouseai = mouseai_instance
        self.host = host
        self.port = port
        self.logger = logging.getLogger(__name__)
        
        # Регистрация маршрутов
        self._register_routes()
        
    def _register_routes(self):
        """Зарегистрировать маршруты API"""
        
        @self.app.route('/api/status', methods=['GET'])
        def get_status():
            """Получить текущий статус системы"""
            if not self.mouseai:
                return jsonify({'error': 'MouseAI не подключен'}), 503
                
            status = self.mouseai.get_status()
            return jsonify(status)
            
        @self.app.route('/api/metrics', methods=['GET'])
        def get_metrics():
            """Получить текущие метрики"""
            if not self.mouseai:
                return jsonify({'error': 'MouseAI не подключен'}), 503
                
            metrics = self.mouseai.get_current_metrics()
            return jsonify(metrics)
            
        @self.app.route('/api/report', methods=['GET'])
        def get_report():
            """Получить отчет за последнюю сессию"""
            if not self.mouseai:
                return jsonify({'error': 'MouseAI не подключен'}), 503
                
            report = self.mouseai.get_latest_report()
            if not report:
                return jsonify({'error': 'Нет данных для отчета'}), 404
                
            return jsonify(report)
            
        @self.app.route('/api/leaderboard', methods=['GET'])
        def get_leaderboard():
            """Получить таблицу лидеров"""
            if not self.mouseai:
                return jsonify({'error': 'MouseAI не подключен'}), 503
                
            metric = request.args.get('metric', 'sample_entropy')
            leaderboard = self.mouseai.get_leaderboard(metric)
            
            return jsonify({
                'metric': metric,
                'leaderboard': leaderboard
            })
            
        @self.app.route('/api/sessions', methods=['GET'])
        def get_sessions():
            """Получить историю сессий"""
            if not self.mouseai:
                return jsonify({'error': 'MouseAI не подключен'}), 503
                
            limit = request.args.get('limit', 10, type=int)
            sessions = self.mouseai.get_session_history(limit)
            
            return jsonify({
                'sessions': sessions,
                'total': len(sessions)
            })
            
        @self.app.route('/api/session/start', methods=['POST'])
        def start_session():
            """Начать новую сессию"""
            if not self.mouseai:
                return jsonify({'error': 'MouseAI не подключен'}), 503
                
            data = request.get_json()
            game = data.get('game')
            duration = data.get('duration', 60)
            
            if not game:
                return jsonify({'error': 'Требуется указать игру'}), 400
                
            try:
                self.mouseai.start_session(game, duration)
                return jsonify({'message': f'Сессия для {game} начата'})
            except Exception as e:
                return jsonify({'error': str(e)}), 500
                
        @self.app.route('/api/session/stop', methods=['POST'])
        def stop_session():
            """Остановить текущую сессию"""
            if not self.mouseai:
                return jsonify({'error': 'MouseAI не подключен'}), 503
                
            try:
                self.mouseai.stop_session()
                return jsonify({'message': 'Сессия остановлена'})
            except Exception as e:
                return jsonify({'error': str(e)}), 500
                
        @self.app.route('/api/config', methods=['GET'])
        def get_config():
            """Получить конфигурацию"""
            if not self.mouseai:
                return jsonify({'error': 'MouseAI не подключен'}), 503
                
            config = self.mouseai.get_config()
            return jsonify(config)
            
        @self.app.route('/api/config', methods=['POST'])
        def update_config():
            """Обновить конфигурацию"""
            if not self.mouseai:
                return jsonify({'error': 'MouseAI не подключен'}), 503
                
            data = request.get_json()
            
            try:
                self.mouseai.update_config(data)
                return jsonify({'message': 'Конфигурация обновлена'})
            except Exception as e:
                return jsonify({'error': str(e)}), 500
                
        @self.app.route('/api/analyze', methods=['POST'])
        def analyze_data():
            """Проанализировать данные"""
            if not self.mouseai:
                return jsonify({'error': 'MouseAI не подключен'}), 503
                
            data = request.get_json()
            
            try:
                result = self.mouseai.analyze_mouse_data(data)
                return jsonify(result)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
                
        @self.app.route('/api/export', methods=['POST'])
        def export_data():
            """Экспортировать данные"""
            if not self.mouseai:
                return jsonify({'error': 'MouseAI не подключен'}), 503
                
            data = request.get_json()
            format_type = data.get('format', 'json')
            output_path = data.get('output_path')
            
            try:
                result = self.mouseai.export_data(format_type, output_path)
                return jsonify({'message': f'Данные экспортированы в {result}'})
            except Exception as e:
                return jsonify({'error': str(e)}), 500
                
        @self.app.route('/api/health', methods=['GET'])
        def health_check():
            """Проверка работоспособности"""
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'mouseai_connected': self.mouseai is not None
            })
            
    def run(self, debug=False):
        """Запустить сервер"""
        self.logger.info(f"🌐 REST API сервер запущен на http://{self.host}:{self.port}")
        
        self.app.run(
            host=self.host,
            port=self.port,
            debug=debug,
            use_reloader=False
        )
        
    def start_async(self):
        """Запустить сервер асинхронно"""
        import threading
        
        def run_server():
            self.run()
            
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        
        self.logger.info("🌐 REST API сервер запущен асинхронно")

class MouseAIAPIManager:
    """Менеджер REST API"""
    
    def __init__(self, mouseai_instance=None):
        self.mouseai = mouseai_instance
        self.api = None
        self.logger = logging.getLogger(__name__)
        
    def start_api(self, host='localhost', port=5000, debug=False):
        """Запустить API"""
        self.api = MouseAIRestAPI(self.mouseai, host, port)
        
        if debug:
            self.api.run(debug=True)
        else:
            self.api.start_async()
            
    def get_api_url(self):
        """Получить URL API"""
        if self.api:
            return f"http://{self.api.host}:{self.api.port}"
        return None
        
    def test_connection(self):
        """Тестировать подключение"""
        import requests
        
        url = self.get_api_url()
        if not url:
            return False
            
        try:
            response = requests.get(f"{url}/api/health", timeout=5)
            return response.status_code == 200
        except Exception:
            return False

def create_rest_api(mouseai_instance=None, host='localhost', port=5000) -> RESTAPI:
    """Создать REST API"""
    return RESTAPI(mouseai_instance, host, port)

def create_api_manager(mouseai_instance=None) -> MouseAIAPIManager:
    """Создать менеджер API"""
    return MouseAIAPIManager(mouseai_instance)

# Пример клиентского кода
MOUSEAI_API_CLIENT = """
import requests
import json

class MouseAIClient:
    def __init__(self, base_url='http://localhost:5000'):
        self.base_url = base_url
        
    def get_status(self):
        response = requests.get(f"{self.base_url}/api/status")
        return response.json()
        
    def get_metrics(self):
        response = requests.get(f"{self.base_url}/api/metrics")
        return response.json()
        
    def start_session(self, game, duration=60):
        data = {'game': game, 'duration': duration}
        response = requests.post(f"{self.base_url}/api/session/start", json=data)
        return response.json()
        
    def stop_session(self):
        response = requests.post(f"{self.base_url}/api/session/stop")
        return response.json()
        
    def get_report(self):
        response = requests.get(f"{self.base_url}/api/report")
        return response.json()
        
    def get_leaderboard(self, metric='sample_entropy'):
        params = {'metric': metric}
        response = requests.get(f"{self.base_url}/api/leaderboard", params=params)
        return response.json()
        
    def analyze_data(self, mouse_data):
        response = requests.post(f"{self.base_url}/api/analyze", json=mouse_data)
        return response.json()
        
    def export_data(self, format_type='json', output_path=None):
        data = {'format': format_type, 'output_path': output_path}
        response = requests.post(f"{self.base_url}/api/export", json=data)
        return response.json()

# Пример использования
if __name__ == "__main__":
    client = MouseAIClient()
    
    # Проверка статуса
    print("Статус:", client.get_status())
    
    # Начало сессии
    print("Начало сессии:", client.start_session("CS2", 120))
    
    # Получение метрик
    print("Метрики:", client.get_metrics())
"""

# Пример использования
if __name__ == "__main__":
    import logging
    
    # Настройка логирования
    logging.basicConfig(level=logging.INFO)
    
    # Создаем API
    api = create_rest_api()
    
    try:
        # Запускаем сервер
        api.run(debug=True)
    except KeyboardInterrupt:
        print("🛑 Остановка REST API сервера...")