#!/usr/bin/env python3
"""
Telegram Bot Integration - Интеграция с Telegram для отчетов и уведомлений
"""

import telegram
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import asyncio
from typing import Dict, List, Optional
import logging
from datetime import datetime

class TelegramBot:
    """Telegram бот для MouseAI"""
    
    def __init__(self, token: str, mouseai_instance=None):
        self.token = token
        self.mouseai = mouseai_instance
        self.logger = logging.getLogger(__name__)
        
        # Конфигурация пользователей
        self.user_config = {}
        self.subscribed_users = set()
        
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Стартовое сообщение"""
        keyboard = [
            [
                InlineKeyboardButton("📊 Статус", callback_data='status'),
                InlineKeyboardButton("📋 Отчет", callback_data='report')
            ],
            [
                InlineKeyboardButton("🏆 Лидеры", callback_data='leaderboard'),
                InlineKeyboardButton("🔔 Подписка", callback_data='subscribe')
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🤖 Добро пожаловать в MouseAI Telegram Bot!\n"
            "Выберите действие:",
            reply_markup=reply_markup
        )
        
    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик кнопок"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        
        if query.data == 'status':
            await self.send_status(query)
        elif query.data == 'report':
            await self.send_report(query)
        elif query.data == 'leaderboard':
            await self.send_leaderboard(query)
        elif query.data == 'subscribe':
            await self.toggle_subscription(query, user_id)
            
    async def send_status(self, query):
        """Отправить статус системы"""
        if not self.mouseai:
            await query.edit_message_text("❌ MouseAI не подключен")
            return
            
        status = self.mouseai.get_status()
        
        message = "📊 *MouseAI Статус*\n\n"
        message += f"🎮 Текущая игра: {status.get('current_game', 'Нет')}\n"
        message += f"⏱️ Сессия: {status.get('session_duration', 0)} сек\n"
        message += f"🎯 Стиль: {status.get('current_style', 'Не определен')}\n\n"
        
        if status.get('metrics'):
            metrics = status['metrics']
            message += "*Метрики:*\n"
            message += f"📈 Sample Entropy: {metrics.get('sample_entropy', 0):.3f}\n"
            message += f"🎯 MAD: {metrics.get('maximum_absolute_deviation', 0):.2f}\n"
            message += f"⚡ TTPV: {metrics.get('time_to_peak_velocity', 0):.3f}\n"
            
        await query.edit_message_text(message, parse_mode='Markdown')
        
    async def send_report(self, query):
        """Отправить отчет за последнюю сессию"""
        if not self.mouseai:
            await query.edit_message_text("❌ MouseAI не подключен")
            return
            
        report = self.mouseai.get_latest_report()
        
        if not report:
            await query.edit_message_text("📝 Нет данных для отчета")
            return
            
        message = "📋 *Отчет о сессии*\n\n"
        message += f"🎮 Игра: {report.get('game', 'Неизвестно')}\n"
        message += f"⏱️ Длительность: {report.get('duration', 0)} сек\n"
        message += f"🎯 Стиль: {report.get('style', 'Не определен')}\n\n"
        
        if 'metrics' in report:
            metrics = report['metrics']
            message += "*Метрики:*\n"
            message += f"📈 Sample Entropy: {metrics.get('sample_entropy', 0):.3f}\n"
            message += f"🎯 MAD: {metrics.get('maximum_absolute_deviation', 0):.2f}\n"
            message += f"⚡ TTPV: {metrics.get('time_to_peak_velocity', 0):.3f}\n"
            message += f"🎯 Efficiency: {metrics.get('movement_efficiency', 0):.3f}\n"
            
        await query.edit_message_text(message, parse_mode='Markdown')
        
    async def send_leaderboard(self, query):
        """Отправить таблицу лидеров"""
        if not self.mouseai:
            await query.edit_message_text("❌ MouseAI не подключен")
            return
            
        leaderboard = self.mouseai.get_leaderboard('sample_entropy')
        
        if not leaderboard:
            await query.edit_message_text("📊 Нет данных для таблицы лидеров")
            return
            
        message = "🏆 *Таблица лидеров*\n\n"
        
        for i, (player, value) in enumerate(leaderboard[:10], 1):
            message += f"{i}. {player} - {value:.3f}\n"
            
        await query.edit_message_text(message, parse_mode='Markdown')
        
    async def toggle_subscription(self, query, user_id: int):
        """Переключить подписку"""
        if user_id in self.subscribed_users:
            self.subscribed_users.remove(user_id)
            message = "❌ Вы отписались от уведомлений"
        else:
            self.subscribed_users.add(user_id)
            message = "✅ Вы подписаны на уведомления"
            
        await query.edit_message_text(message)
        
    async def send_notification(self, message: str):
        """Отправить уведомление всем подписчикам"""
        for user_id in self.subscribed_users:
            try:
                await self.application.bot.send_message(
                    chat_id=user_id,
                    text=message
                )
            except Exception as e:
                self.logger.error(f"Ошибка отправки уведомления пользователю {user_id}: {e}")
                
    async def send_session_notification(self, session_data: Dict):
        """Отправить уведомление о начале сессии"""
        message = f"🎮 Начата сессия анализа: {session_data.get('game', 'Неизвестно')}"
        await self.send_notification(message)
        
    async def send_metrics_update(self, metrics: Dict):
        """Отправить обновление метрик"""
        message = "📊 *Обновление метрик*\n\n"
        message += f"📈 Sample Entropy: {metrics.get('sample_entropy', 0):.3f}\n"
        message += f"🎯 MAD: {metrics.get('maximum_absolute_deviation', 0):.2f}\n"
        message += f"⚡ TTPV: {metrics.get('time_to_peak_velocity', 0):.3f}\n"
        
        await self.send_notification(message)
        
    async def send_session_report(self, report: Dict):
        """Отправить отчет о сессии"""
        message = "📋 *Отчет о сессии*\n\n"
        message += f"🎮 Игра: {report.get('game', 'Неизвестно')}\n"
        message += f"⏱️ Длительность: {report.get('duration', 0)} сек\n"
        message += f"🎯 Стиль: {report.get('style', 'Не определен')}\n\n"
        
        if 'metrics' in report:
            metrics = report['metrics']
            message += "*Метрики:*\n"
            message += f"📈 Sample Entropy: {metrics.get('sample_entropy', 0):.3f}\n"
            message += f"🎯 MAD: {metrics.get('maximum_absolute_deviation', 0):.2f}\n"
            message += f"⚡ TTPV: {metrics.get('time_to_peak_velocity', 0):.3f}\n"
            
        await self.send_notification(message)
        
    async def run(self):
        """Запустить Telegram бота"""
        self.application = Application.builder().token(self.token).build()
        
        # Регистрация обработчиков
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CallbackQueryHandler(self.button_handler))
        
        # Запуск бота
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()
        
        self.logger.info("🤖 Telegram бот запущен")
        
        # Ожидание завершения
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            await self.application.stop()
            await self.application.shutdown()

def create_telegram_bot(token: str, mouseai_instance=None) -> TelegramBot:
    """Создать Telegram бота"""
    return TelegramBot(token, mouseai_instance)

# Пример использования
if __name__ == "__main__":
    import os
    
    # Получаем токен из переменной окружения
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not token:
        print("❌ Установите TELEGRAM_BOT_TOKEN")
        exit(1)
        
    bot = create_telegram_bot(token)
    
    try:
        asyncio.run(bot.run())
    except KeyboardInterrupt:
        print("� Остановка Telegram бота...")