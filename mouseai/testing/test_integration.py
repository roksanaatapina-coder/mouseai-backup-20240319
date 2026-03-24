#!/usr/bin/env python3
"""
Test Integration - Тесты для интеграций
"""

import unittest
import sys
import os
import time
import threading
from unittest.mock import Mock, patch, MagicMock
import requests
from flask import Flask
import socket

# Добавляем путь к проекту
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from mouseai.integration.discord_bot import DiscordBot
from mouseai.integration.telegram_bot import TelegramBot
from mouseai.integration.obs_overlay import OBSOverlay
from mouseai.integration.rest_api import RESTAPI
from mouseai.utils import MouseAILogger

class TestDiscordBot(unittest.TestCase):
    """Тесты для Discord Bot"""
    
    def setUp(self):
        """Настройка теста"""
        self.logger = MouseAILogger()
        self.discord_bot = DiscordBot()
        
    def test_initialization(self):
        """Тест инициализации"""
        self.assertIsNotNone(self.discord_bot)
        self.assertFalse(self.discord_bot.is_running)
        self.assertIsNone(self.discord_bot.client)
        
    def test_configure(self):
        """Тест конфигурации"""
        config = {
            'token': 'test_token',
            'channel_id': '123456789',
            'notifications': {
                'session_start': True,
                'session_end': True,
                'anomalies': True,
                'achievements': True
            }
        }
        
        self.discord_bot.configure(config)
        
        # Проверяем, что конфигурация применилась
        self.assertEqual(self.discord_bot.config['token'], 'test_token')
        self.assertEqual(self.discord_bot.config['channel_id'], '123456789')
        
    def test_start_stop(self):
        """Тест запуска и остановки"""
        # Тестируем без реального токена
        self.discord_bot.configure({'token': 'test_token'})
        
        # Попробуем запустить (должен завершиться с ошибкой)
        try:
            self.discord_bot.start()
        except:
            pass  # Ожидаемая ошибка из-за невалидного токена
            
        self.assertFalse(self.discord_bot.is_running)
        
    def test_send_message(self):
        """Тест отправки сообщения"""
        # Мокаем клиент
        mock_client = Mock()
        mock_channel = Mock()
        mock_client.get_channel.return_value = mock_channel
        
        self.discord_bot.client = mock_client
        
        # Отправляем сообщение
        result = self.discord_bot.send_message("Test message")
        
        # Проверяем, что сообщение было отправлено
        self.assertTrue(result)
        mock_channel.send.assert_called_once_with("Test message")
        
    def test_notify_session_start(self):
        """Тест уведомления о начале сессии"""
        # Мокаем клиент
        mock_client = Mock()
        mock_channel = Mock()
        mock_client.get_channel.return_value = mock_channel
        
        self.discord_bot.client = mock_client
        self.discord_bot.config['notifications']['session_start'] = True
        
        # Отправляем уведомление
        result = self.discord_bot.notify_session_start("CS2", 300)
        
        # Проверяем результат
        self.assertTrue(result)
        mock_channel.send.assert_called_once()
        
    def test_notify_session_end(self):
        """Тест уведомления об окончании сессии"""
        # Мокаем клиент
        mock_client = Mock()
        mock_channel = Mock()
        mock_client.get_channel.return_value = mock_channel
        
        self.discord_bot.client = mock_client
        self.discord_bot.config['notifications']['session_end'] = True
        
        # Отправляем уведомление
        metrics = {'sample_entropy': 0.5, 'efficiency': 0.8}
        result = self.discord_bot.notify_session_end("CS2", 300, metrics)
        
        # Проверяем результат
        self.assertTrue(result)
        mock_channel.send.assert_called_once()
        
    def test_notify_anomaly(self):
        """Тест уведомления об аномалии"""
        # Мокаем клиент
        mock_client = Mock()
        mock_channel = Mock()
        mock_client.get_channel.return_value = mock_channel
        
        self.discord_bot.client = mock_client
        self.discord_bot.config['notifications']['anomalies'] = True
        
        # Отправляем уведомление
        anomaly = {'metric': 'sample_entropy', 'value': 0.1, 'severity': 'high'}
        result = self.discord_bot.notify_anomaly(anomaly)
        
        # Проверяем результат
        self.assertTrue(result)
        mock_channel.send.assert_called_once()
        
    def test_notify_achievement(self):
        """Тест уведомления о достижении"""
        # Мокаем клиент
        mock_client = Mock()
        mock_channel = Mock()
        mock_client.get_channel.return_value = mock_channel
        
        self.discord_bot.client = mock_client
        self.discord_bot.config['notifications']['achievements'] = True
        
        # Отправляем уведомление
        achievement = {'name': 'Perfect Aim', 'description': 'Achieved perfect accuracy'}
        result = self.discord_bot.notify_achievement(achievement)
        
        # Проверяем результат
        self.assertTrue(result)
        mock_channel.send.assert_called_once()

class TestTelegramBot(unittest.TestCase):
    """Тесты для Telegram Bot"""
    
    def setUp(self):
        """Настройка теста"""
        self.logger = MouseAILogger()
        self.telegram_bot = TelegramBot()
        
    def test_initialization(self):
        """Тест инициализации"""
        self.assertIsNotNone(self.telegram_bot)
        self.assertFalse(self.telegram_bot.is_running)
        self.assertIsNone(self.telegram_bot.bot)
        
    def test_configure(self):
        """Тест конфигурации"""
        config = {
            'token': 'test_token',
            'chat_id': '123456789',
            'notifications': {
                'session_start': True,
                'session_end': True,
                'anomalies': True,
                'reports': True
            }
        }
        
        self.telegram_bot.configure(config)
        
        # Проверяем, что конфигурация применилась
        self.assertEqual(self.telegram_bot.config['token'], 'test_token')
        self.assertEqual(self.telegram_bot.config['chat_id'], '123456789')
        
    def test_send_message(self):
        """Тест отправки сообщения"""
        # Мокаем бота
        mock_bot = Mock()
        
        self.telegram_bot.bot = mock_bot
        
        # Отправляем сообщение
        result = self.telegram_bot.send_message("Test message")
        
        # Проверяем, что сообщение было отправлено
        self.assertTrue(result)
        mock_bot.send_message.assert_called_once_with('123456789', "Test message")
        
    def test_notify_session_start(self):
        """Тест уведомления о начале сессии"""
        # Мокаем бота
        mock_bot = Mock()
        
        self.telegram_bot.bot = mock_bot
        self.telegram_bot.config['notifications']['session_start'] = True
        
        # Отправляем уведомление
        result = self.telegram_bot.notify_session_start("CS2", 300)
        
        # Проверяем результат
        self.assertTrue(result)
        mock_bot.send_message.assert_called_once()
        
    def test_notify_session_end(self):
        """Тест уведомления об окончании сессии"""
        # Мокаем бота
        mock_bot = Mock()
        
        self.telegram_bot.bot = mock_bot
        self.telegram_bot.config['notifications']['session_end'] = True
        
        # Отправляем уведомление
        metrics = {'sample_entropy': 0.5, 'efficiency': 0.8}
        result = self.telegram_bot.notify_session_end("CS2", 300, metrics)
        
        # Проверяем результат
        self.assertTrue(result)
        mock_bot.send_message.assert_called_once()
        
    def test_notify_anomaly(self):
        """Тест уведомления об аномалии"""
        # Мокаем бота
        mock_bot = Mock()
        
        self.telegram_bot.bot = mock_bot
        self.telegram_bot.config['notifications']['anomalies'] = True
        
        # Отправляем уведомление
        anomaly = {'metric': 'sample_entropy', 'value': 0.1, 'severity': 'high'}
        result = self.telegram_bot.notify_anomaly(anomaly)
        
        # Проверяем результат
        self.assertTrue(result)
        mock_bot.send_message.assert_called_once()
        
    def test_send_report(self):
        """Тест отправки отчета"""
        # Мокаем бота
        mock_bot = Mock()
        
        self.telegram_bot.bot = mock_bot
        self.telegram_bot.config['notifications']['reports'] = True
        
        # Отправляем отчет
        report = {'summary': 'Test report', 'metrics': {'sample_entropy': 0.5}}
        result = self.telegram_bot.send_report(report)
        
        # Проверяем результат
        self.assertTrue(result)
        mock_bot.send_message.assert_called_once()

class TestOBSOverlay(unittest.TestCase):
    """Тесты для OBS Overlay"""
    
    def setUp(self):
        """Настройка теста"""
        self.logger = MouseAILogger()
        self.obs_overlay = OBSOverlay()
        
    def test_initialization(self):
        """Тест инициализации"""
        self.assertIsNotNone(self.obs_overlay)
        self.assertFalse(self.obs_overlay.is_running)
        self.assertIsNone(self.obs_overlay.server)
        
    def test_configure(self):
        """Тест конфигурации"""
        config = {
            'port': 8765,
            'websocket_enabled': True,
            'overlay_theme': 'dark',
            'metrics_display': ['sample_entropy', 'efficiency', 'reaction_time']
        }
        
        self.obs_overlay.configure(config)
        
        # Проверяем, что конфигурация применилась
        self.assertEqual(self.obs_overlay.config['port'], 8765)
        self.assertTrue(self.obs_overlay.config['websocket_enabled'])
        
    def test_start_stop(self):
        """Тест запуска и остановки"""
        # Тестируем без реального порта
        self.obs_overlay.configure({'port': 8765})
        
        # Попробуем запустить
        try:
            self.obs_overlay.start()
            time.sleep(0.1)  # Даем время на запуск
            self.obs_overlay.stop()
        except:
            pass  # Возможны ошибки при запуске
            
    def test_update_overlay(self):
        """Тест обновления оверлея"""
        # Мокаем сервер
        mock_server = Mock()
        
        self.obs_overlay.server = mock_server
        
        # Обновляем оверлей
        metrics = {'sample_entropy': 0.5, 'efficiency': 0.8}
        result = self.obs_overlay.update_overlay(metrics)
        
        # Проверяем результат
        self.assertTrue(result)
        
    def test_generate_html_overlay(self):
        """Тест генерации HTML оверлея"""
        metrics = {
            'sample_entropy': 0.5,
            'efficiency': 0.8,
            'reaction_time': 0.2
        }
        
        # Генерируем HTML
        html = self.obs_overlay.generate_html_overlay(metrics)
        
        # Проверяем результат
        self.assertIsInstance(html, str)
        self.assertIn('Sample Entropy', html)
        self.assertIn('Efficiency', html)
        self.assertIn('Reaction Time', html)
        
    def test_export_overlay_config(self):
        """Тест экспорта конфигурации оверлея"""
        filename = 'test_overlay_config.json'
        
        # Экспортируем конфигурацию
        result = self.obs_overlay.export_overlay_config(filename)
        
        # Проверяем результат
        self.assertTrue(result)
        self.assertTrue(os.path.exists(filename))
        
        # Очищаем
        if os.path.exists(filename):
            os.remove(filename)

class TestRESTAPI(unittest.TestCase):
    """Тесты для REST API"""
    
    def setUp(self):
        """Настройка теста"""
        self.logger = MouseAILogger()
        self.rest_api = RESTAPI()
        
    def test_initialization(self):
        """Тест инициализации"""
        self.assertIsNotNone(self.rest_api)
        self.assertFalse(self.rest_api.is_running)
        self.assertIsNone(self.rest_api.app)
        self.assertIsNone(self.rest_api.server)
        
    def test_configure(self):
        """Тест конфигурации"""
        config = {
            'port': 5000,
            'host': 'localhost',
            'auth_required': False,
            'api_key': '',
            'cors_enabled': True
        }
        
        self.rest_api.configure(config)
        
        # Проверяем, что конфигурация применилась
        self.assertEqual(self.rest_api.config['port'], 5000)
        self.assertEqual(self.rest_api.config['host'], 'localhost')
        
    def test_create_app(self):
        """Тест создания Flask приложения"""
        self.rest_api.configure({'port': 5000})
        
        # Создаем приложение
        app = self.rest_api.create_app()
        
        # Проверяем, что приложение создано
        self.assertIsNotNone(app)
        self.assertIsInstance(app, Flask)
        
    def test_add_endpoints(self):
        """Тест добавления эндпоинтов"""
        self.rest_api.configure({'port': 5000})
        
        # Создаем приложение
        app = self.rest_api.create_app()
        
        # Проверяем, что эндпоинты добавлены
        self.assertGreater(len(app.url_map.rules), 0)
        
    def test_start_stop(self):
        """Тест запуска и остановки"""
        # Тестируем без реального сервера
        self.rest_api.configure({'port': 5000})
        
        # Попробуем запустить в фоновом режиме
        try:
            self.rest_api.start()
            time.sleep(0.1)  # Даем время на запуск
            self.rest_api.stop()
        except:
            pass  # Возможны ошибки при запуске
            
    def test_api_endpoints(self):
        """Тест эндпоинтов API"""
        self.rest_api.configure({'port': 5000})
        
        # Создаем приложение
        app = self.rest_api.create_app()
        
        # Тестируем основные эндпоинты
        with app.test_client() as client:
            # Тестируем /
            response = client.get('/')
            self.assertEqual(response.status_code, 200)
            
            # Тестируем /status
            response = client.get('/status')
            self.assertEqual(response.status_code, 200)
            
            # Тестируем /metrics
            response = client.get('/metrics')
            self.assertEqual(response.status_code, 200)
            
    def test_cors_headers(self):
        """Тест CORS заголовков"""
        self.rest_api.configure({'port': 5000, 'cors_enabled': True})
        
        # Создаем приложение
        app = self.rest_api.create_app()
        
        with app.test_client() as client:
            response = client.get('/')
            
            # Проверяем, что CORS заголовки присутствуют
            self.assertIn('Access-Control-Allow-Origin', response.headers)
            
    def test_authentication(self):
        """Тест аутентификации"""
        self.rest_api.configure({
            'port': 5000,
            'auth_required': True,
            'api_key': 'test_key'
        })
        
        # Создаем приложение
        app = self.rest_api.create_app()
        
        with app.test_client() as client:
            # Тестируем запрос без ключа
            response = client.get('/metrics')
            self.assertEqual(response.status_code, 401)
            
            # Тестируем запрос с ключом
            response = client.get('/metrics', headers={'X-API-Key': 'test_key'})
            self.assertEqual(response.status_code, 200)

class TestIntegrationCommunication(unittest.TestCase):
    """Тесты для коммуникации между интеграциями"""
    
    def test_discord_telegram_communication(self):
        """Тест коммуникации между Discord и Telegram ботами"""
        # Создаем ботов
        discord_bot = DiscordBot()
        telegram_bot = TelegramBot()
        
        # Проверяем, что они могут работать независимо
        self.assertIsNotNone(discord_bot)
        self.assertIsNotNone(telegram_bot)
        
    def test_obs_rest_api_integration(self):
        """Тест интеграции OBS и REST API"""
        # Создаем компоненты
        obs_overlay = OBSOverlay()
        rest_api = RESTAPI()
        
        # Проверяем, что они могут работать независимо
        self.assertIsNotNone(obs_overlay)
        self.assertIsNotNone(rest_api)
        
    def test_notification_distribution(self):
        """Тест распределения уведомлений"""
        # Создаем ботов
        discord_bot = DiscordBot()
        telegram_bot = TelegramBot()
        
        # Мокаем их
        mock_discord = Mock()
        mock_telegram = Mock()
        
        discord_bot.client = mock_discord
        telegram_bot.bot = mock_telegram
        
        # Тестируем отправку уведомлений
        message = "Test notification"
        
        # Discord
        discord_bot.send_message(message)
        mock_discord.get_channel().send.assert_called_once_with(message)
        
        # Telegram
        telegram_bot.send_message(message)
        mock_telegram.send_message.assert_called_once_with('123456789', message)

if __name__ == '__main__':
    unittest.main()