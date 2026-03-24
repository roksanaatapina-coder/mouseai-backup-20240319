#!/usr/bin/env python3
"""
OBS Overlay Integration - Интеграция с OBS для отображения метрик в реальном времени
"""

import asyncio
import websockets
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime

class OBSOverlayServer:
    """WebSocket сервер для OBS overlay"""
    
    def __init__(self, host='localhost', port=8765, mouseai_instance=None):
        self.host = host
        self.port = port
        self.mouseai = mouseai_instance
        self.logger = logging.getLogger(__name__)
        
        # Подключенные клиенты
        self.clients = set()
        
        # Текущие метрики
        self.current_metrics = {}
        self.current_status = {}
        
    async def handler(self, websocket, path):
        """Обработчик WebSocket соединений"""
        self.clients.add(websocket)
        self.logger.info(f"🔌 Клиент подключен: {websocket.remote_address}")
        
        try:
            # Отправляем текущие данные новому клиенту
            if self.current_metrics:
                await websocket.send(json.dumps({
                    'type': 'metrics_update',
                    'data': self.current_metrics
                }))
                
            if self.current_status:
                await websocket.send(json.dumps({
                    'type': 'status_update',
                    'data': self.current_status
                }))
                
            # Поддерживаем соединение
            async for message in websocket:
                try:
                    data = json.loads(message)
                    await self.handle_client_message(websocket, data)
                except json.JSONDecodeError:
                    self.logger.warning(f"❌ Неверный JSON от клиента: {message}")
                    
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            self.clients.remove(websocket)
            self.logger.info(f"🔌 Клиент отключен: {websocket.remote_address}")
            
    async def handle_client_message(self, websocket, data: Dict):
        """Обработать сообщение от клиента"""
        message_type = data.get('type')
        
        if message_type == 'request_status':
            if self.current_status:
                await websocket.send(json.dumps({
                    'type': 'status_update',
                    'data': self.current_status
                }))
                
        elif message_type == 'request_metrics':
            if self.current_metrics:
                await websocket.send(json.dumps({
                    'type': 'metrics_update',
                    'data': self.current_metrics
                }))
                
    async def broadcast_metrics(self, metrics: Dict):
        """Транслировать метрики всем клиентам"""
        self.current_metrics = metrics
        
        message = json.dumps({
            'type': 'metrics_update',
            'data': metrics
        })
        
        # Отправляем всем подключенным клиентам
        if self.clients:
            await asyncio.gather(
                *[client.send(message) for client in self.clients],
                return_exceptions=True
            )
            
    async def broadcast_status(self, status: Dict):
        """Транслировать статус всем клиентам"""
        self.current_status = status
        
        message = json.dumps({
            'type': 'status_update',
            'data': status
        })
        
        # Отправляем всем подключенным клиентам
        if self.clients:
            await asyncio.gather(
                *[client.send(message) for client in self.clients],
                return_exceptions=True
            )
            
    async def start_server(self):
        """Запустить WebSocket сервер"""
        server = await websockets.serve(
            self.handler,
            self.host,
            self.port
        )
        
        self.logger.info(f"🌐 OBS Overlay сервер запущен на ws://{self.host}:{self.port}")
        
        return server
        
    async def run(self):
        """Запустить сервер"""
        server = await self.start_server()
        
        try:
            await server.wait_closed()
        except KeyboardInterrupt:
            pass
        finally:
            server.close()
            await server.wait_closed()

class OBSOverlayClient:
    """Клиент для OBS overlay"""
    
    def __init__(self, uri='ws://localhost:8765'):
        self.uri = uri
        self.websocket = None
        self.logger = logging.getLogger(__name__)
        
        # Обработчики событий
        self.on_metrics_update = None
        self.on_status_update = None
        
    async def connect(self):
        """Подключиться к серверу"""
        try:
            self.websocket = await websockets.connect(self.uri)
            self.logger.info(f"🔌 Подключено к {self.uri}")
            
            # Запрашиваем текущие данные
            await self.request_status()
            await self.request_metrics()
            
            # Начинаем слушать сообщения
            await self.listen()
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка подключения: {e}")
            
    async def disconnect(self):
        """Отключиться от сервера"""
        if self.websocket:
            await self.websocket.close()
            self.logger.info("🔌 Отключено от сервера")
            
    async def listen(self):
        """Слушать сообщения от сервера"""
        try:
            async for message in self.websocket:
                data = json.loads(message)
                await self.handle_server_message(data)
        except websockets.exceptions.ConnectionClosed:
            self.logger.warning("🔌 Соединение с сервером закрыто")
        except Exception as e:
            self.logger.error(f"❌ Ошибка при прослушивании: {e}")
            
    async def handle_server_message(self, data: Dict):
        """Обработать сообщение от сервера"""
        message_type = data.get('type')
        message_data = data.get('data', {})
        
        if message_type == 'metrics_update' and self.on_metrics_update:
            await self.on_metrics_update(message_data)
            
        elif message_type == 'status_update' and self.on_status_update:
            await self.on_status_update(message_data)
            
    async def request_status(self):
        """Запросить статус"""
        if self.websocket:
            await self.websocket.send(json.dumps({
                'type': 'request_status'
            }))
            
    async def request_metrics(self):
        """Запросить метрики"""
        if self.websocket:
            await self.websocket.send(json.dumps({
                'type': 'request_metrics'
            }))
            
    async def send_command(self, command: str, data: Dict = None):
        """Отправить команду серверу"""
        if self.websocket:
            message = {
                'type': 'command',
                'command': command
            }
            
            if data:
                message['data'] = data
                
            await self.websocket.send(json.dumps(message))

class OBSOverlayManager:
    """Менеджер OBS overlay"""
    
    def __init__(self, mouseai_instance=None):
        self.mouseai = mouseai_instance
        self.server = None
        self.client = None
        self.logger = logging.getLogger(__name__)
        
    async def start_server(self, host='localhost', port=8765):
        """Запустить сервер"""
        self.server = OBSOverlayServer(host, port, self.mouseai)
        
        # Подключаем обработчики
        if self.mouseai:
            self.mouseai.on_metrics_update = self.server.broadcast_metrics
            self.mouseai.on_status_update = self.server.broadcast_status
            
        await self.server.run()
        
    async def start_client(self, uri='ws://localhost:8765'):
        """Запустить клиент"""
        self.client = OBSOverlayClient(uri)
        
        # Подключаем обработчики
        if self.mouseai:
            self.client.on_metrics_update = self.handle_metrics_update
            self.client.on_status_update = self.handle_status_update
            
        await self.client.connect()
        
    async def handle_metrics_update(self, metrics: Dict):
        """Обработать обновление метрик"""
        self.logger.info(f"📊 Получены метрики: {metrics}")
        
        # Можно добавить логику обработки метрик
        if self.mouseai:
            self.mouseai.update_overlay_metrics(metrics)
            
    async def handle_status_update(self, status: Dict):
        """Обработать обновление статуса"""
        self.logger.info(f"ℹ️ Получен статус: {status}")
        
        # Можно добавить логику обработки статуса
        if self.mouseai:
            self.mouseai.update_overlay_status(status)

class OBSOverlay:
    """OBS Overlay для MouseAI"""
    
    def __init__(self, host='localhost', port=8765, mouseai_instance=None):
        self.server = OBSOverlayServer(host, port, mouseai_instance)
        self.client = OBSOverlayClient(f'ws://{host}:{port}')
        
    async def start_server(self):
        """Запустить сервер"""
        await self.server.run()
        
    async def start_client(self):
        """Запустить клиент"""
        await self.client.connect()
        
    async def broadcast_metrics(self, metrics: Dict):
        """Транслировать метрики"""
        await self.server.broadcast_metrics(metrics)
        
    async def broadcast_status(self, status: Dict):
        """Транслировать статус"""
        await self.server.broadcast_status(status)

def create_obs_overlay(host='localhost', port=8765, mouseai_instance=None) -> OBSOverlay:
    """Создать OBS overlay"""
    return OBSOverlay(host, port, mouseai_instance)

# Пример HTML для OBS overlay
OBS_OVERLAY_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>MouseAI Overlay</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: rgba(0, 0, 0, 0.8);
            color: white;
            margin: 0;
            padding: 20px;
            text-shadow: 1px 1px 2px black;
        }
        
        .container {
            max-width: 400px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            margin-bottom: 20px;
            border-bottom: 2px solid #007bff;
            padding-bottom: 10px;
        }
        
        .status {
            background: #2d3436;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            border: 1px solid #636e72;
        }
        
        .metrics {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
        }
        
        .metric-card {
            background: #2d3436;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #007bff;
            text-align: center;
        }
        
        .metric-value {
            font-size: 24px;
            font-weight: bold;
            color: #007bff;
        }
        
        .metric-label {
            font-size: 12px;
            color: #b2bec3;
            text-transform: uppercase;
        }
        
        .connection-status {
            position: absolute;
            top: 10px;
            right: 10px;
            width: 10px;
            height: 10px;
            background: red;
            border-radius: 50%;
            box-shadow: 0 0 10px red;
        }
        
        .connected {
            background: green;
            box-shadow: 0 0 10px green;
        }
    </style>
</head>
<body>
    <div class="connection-status" id="connectionStatus"></div>
    
    <div class="container">
        <div class="header">
            <h1>🎯 MouseAI</h1>
            <p>Real-time Metrics</p>
        </div>
        
        <div class="status" id="statusPanel">
            <div><strong>Game:</strong> <span id="gameName">-</span></div>
            <div><strong>Style:</strong> <span id="styleName">-</span></div>
            <div><strong>Duration:</strong> <span id="sessionDuration">0s</span></div>
        </div>
        
        <div class="metrics">
            <div class="metric-card">
                <div class="metric-value" id="sampleEntropy">0.000</div>
                <div class="metric-label">Sample Entropy</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-value" id="mad">0.00</div>
                <div class="metric-label">MAD</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-value" id="ttpv">0.000</div>
                <div class="metric-label">TTPV</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-value" id="efficiency">0.000</div>
                <div class="metric-label">Efficiency</div>
            </div>
        </div>
    </div>
    
    <script>
        const ws = new WebSocket('ws://localhost:8765');
        const connectionStatus = document.getElementById('connectionStatus');
        
        ws.onopen = () => {
            connectionStatus.classList.add('connected');
            console.log('WebSocket connected');
        };
        
        ws.onclose = () => {
            connectionStatus.classList.remove('connected');
            console.log('WebSocket disconnected');
        };
        
        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            
            if (data.type === 'status_update') {
                updateStatus(data.data);
            } else if (data.type === 'metrics_update') {
                updateMetrics(data.data);
            }
        };
        
        function updateStatus(status) {
            document.getElementById('gameName').textContent = status.current_game || '-';
            document.getElementById('styleName').textContent = status.current_style || '-';
            document.getElementById('sessionDuration').textContent = status.session_duration + 's';
        }
        
        function updateMetrics(metrics) {
            document.getElementById('sampleEntropy').textContent = (metrics.sample_entropy || 0).toFixed(3);
            document.getElementById('mad').textContent = (metrics.maximum_absolute_deviation || 0).toFixed(2);
            document.getElementById('ttpv').textContent = (metrics.time_to_peak_velocity || 0).toFixed(3);
            document.getElementById('efficiency').textContent = (metrics.movement_efficiency || 0).toFixed(3);
        }
    </script>
</body>
</html>
"""

# Пример использования
if __name__ == "__main__":
    import asyncio
    
    async def main():
        # Создаем сервер
        server = create_obs_overlay()
        
        try:
            await server.run()
        except KeyboardInterrupt:
            print("🛑 Остановка OBS overlay сервера...")
            
    asyncio.run(main())
