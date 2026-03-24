#!/usr/bin/env python3
"""
Discord Bot Integration - Интеграция с Discord для отчетов и уведомлений
"""

import discord
from discord.ext import commands, tasks
from discord import app_commands
import asyncio
from typing import Dict, List, Optional
import json
import logging
from datetime import datetime, timedelta

class DiscordBot(commands.Bot):
    """Discord бот для MouseAI"""
    
    def __init__(self, token: str, mouseai_instance=None):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        
        super().__init__(command_prefix='!', intents=intents)
        
        self.token = token
        self.mouseai = mouseai_instance
        self.logger = logging.getLogger(__name__)
        
        # Настройки сервера
        self.server_config = {}
        self.active_sessions = {}
        
    async def setup_hook(self):
        """Настройка бота"""
        self.logger.info("🤖 Discord бот инициализирован")
        
        # Регистрация slash-команд
        await self.tree.sync()
        
        # Запуск фоновых задач
        self.status_updater.start()
        
    @tasks.loop(minutes=5)
    async def status_updater(self):
        """Обновление статуса бота"""
        if self.mouseai:
            status = self.mouseai.get_status()
            activity = discord.Game(name=f"Анализ: {status.get('current_game', 'None')}")
            await self.change_presence(activity=activity)
            
    @status_updater.before_loop
    async def before_status_updater(self):
        await self.wait_until_ready()
        
    @app_commands.command(name="status", description="Показать статус MouseAI")
    async def cmd_status(self, interaction: discord.Interaction):
        """Показать текущий статус системы"""
        await interaction.response.defer()
        
        if not self.mouseai:
            await interaction.followup.send("❌ MouseAI не подключен")
            return
            
        status = self.mouseai.get_status()
        
        embed = discord.Embed(
            title="📊 MouseAI Статус",
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )
        
        embed.add_field(name="🎮 Текущая игра", value=status.get('current_game', 'Нет'), inline=True)
        embed.add_field(name="⏱️ Сессия", value=f"{status.get('session_duration', 0)} сек", inline=True)
        embed.add_field(name="🎯 Стиль", value=status.get('current_style', 'Не определен'), inline=True)
        
        if status.get('metrics'):
            metrics = status['metrics']
            embed.add_field(name="📈 Sample Entropy", value=f"{metrics.get('sample_entropy', 0):.3f}", inline=True)
            embed.add_field(name="🎯 MAD", value=f"{metrics.get('maximum_absolute_deviation', 0):.2f}", inline=True)
            embed.add_field(name="⚡ TTPV", value=f"{metrics.get('time_to_peak_velocity', 0):.3f}", inline=True)
            
        await interaction.followup.send(embed=embed)
        
    @app_commands.command(name="report", description="Показать отчет за последнюю сессию")
    async def cmd_report(self, interaction: discord.Interaction):
        """Показать отчет за последнюю сессию"""
        await interaction.response.defer()
        
        if not self.mouseai:
            await interaction.followup.send("❌ MouseAI не подключен")
            return
            
        report = self.mouseai.get_latest_report()
        
        if not report:
            await interaction.followup.send("📝 Нет данных для отчета")
            return
            
        embed = discord.Embed(
            title="📋 Отчет о сессии",
            color=discord.Color.green(),
            timestamp=datetime.now()
        )
        
        embed.add_field(name="🎮 Игра", value=report.get('game', 'Неизвестно'), inline=True)
        embed.add_field(name="⏱️ Длительность", value=f"{report.get('duration', 0)} сек", inline=True)
        embed.add_field(name="🎯 Стиль", value=report.get('style', 'Не определен'), inline=True)
        
        if 'metrics' in report:
            metrics = report['metrics']
            embed.add_field(name="📈 Sample Entropy", value=f"{metrics.get('sample_entropy', 0):.3f}", inline=True)
            embed.add_field(name="🎯 Maximum Absolute Deviation", value=f"{metrics.get('maximum_absolute_deviation', 0):.2f}", inline=True)
            embed.add_field(name="⚡ Time to Peak Velocity", value=f"{metrics.get('time_to_peak_velocity', 0):.3f}", inline=True)
            embed.add_field(name="🎯 Movement Efficiency", value=f"{metrics.get('movement_efficiency', 0):.3f}", inline=True)
            
        await interaction.followup.send(embed=embed)
        
    @app_commands.command(name="leaderboard", description="Показать таблицу лидеров")
    async def cmd_leaderboard(self, interaction: discord.Interaction, metric: str = "sample_entropy"):
        """Показать таблицу лидеров по метрике"""
        await interaction.response.defer()
        
        if not self.mouseai:
            await interaction.followup.send("❌ MouseAI не подключен")
            return
            
        leaderboard = self.mouseai.get_leaderboard(metric)
        
        if not leaderboard:
            await interaction.followup.send(f"📊 Нет данных для метрики: {metric}")
            return
            
        embed = discord.Embed(
            title=f"🏆 Таблица лидеров: {metric}",
            color=discord.Color.gold(),
            timestamp=datetime.now()
        )
        
        for i, (player, value) in enumerate(leaderboard[:10], 1):
            embed.add_field(
                name=f"{i}. {player}", 
                value=f"{value:.3f}", 
                inline=False
            )
            
        await interaction.followup.send(embed=embed)
        
    @app_commands.command(name="subscribe", description="Подписаться на уведомления")
    async def cmd_subscribe(self, interaction: discord.Interaction):
        """Подписаться на уведомления о сессиях"""
        channel = interaction.channel
        
        if channel.id not in self.server_config:
            self.server_config[channel.id] = {
                'notifications': True,
                'metrics': True,
                'reports': True
            }
            
        await interaction.response.send_message("✅ Вы подписаны на уведомления!")
        
    @app_commands.command(name="unsubscribe", description="Отписаться от уведомлений")
    async def cmd_unsubscribe(self, interaction: discord.Interaction):
        """Отписаться от уведомлений"""
        channel = interaction.channel
        
        if channel.id in self.server_config:
            del self.server_config[channel.id]
            
        await interaction.response.send_message("❌ Вы отписаны от уведомлений!")
        
    @app_commands.command(name="help", description="Показать помощь по командам")
    async def cmd_help(self, interaction: discord.Interaction):
        """Показать помощь по командам"""
        embed = discord.Embed(
            title="🤖 MouseAI Discord Bot",
            description="Команды для управления MouseAI через Discord",
            color=discord.Color.blue()
        )
        
        commands_list = [
            "/status - Показать текущий статус системы",
            "/report - Показать отчет за последнюю сессию",
            "/leaderboard [metric] - Показать таблицу лидеров",
            "/subscribe - Подписаться на уведомления",
            "/unsubscribe - Отписаться от уведомлений",
            "/help - Показать эту помощь"
        ]
        
        embed.add_field(
            name="📋 Доступные команды",
            value="\n".join(commands_list),
            inline=False
        )
        
        embed.add_field(
            name="📊 Доступные метрики",
            value="sample_entropy, maximum_absolute_deviation, time_to_peak_velocity, movement_efficiency",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)
        
    async def send_session_notification(self, session_data: Dict):
        """Отправить уведомление о начале сессии"""
        message = f"🎮 Начата сессия анализа: {session_data.get('game', 'Неизвестно')}"
        
        for channel_id, config in self.server_config.items():
            if config.get('notifications', False):
                try:
                    channel = self.get_channel(channel_id)
                    if channel:
                        await channel.send(message)
                except Exception as e:
                    self.logger.error(f"Ошибка отправки уведомления: {e}")
                    
    async def send_metrics_update(self, metrics: Dict):
        """Отправить обновление метрик"""
        message = f"📊 Обновление метрик:\n"
        message += f"• Sample Entropy: {metrics.get('sample_entropy', 0):.3f}\n"
        message += f"• MAD: {metrics.get('maximum_absolute_deviation', 0):.2f}\n"
        message += f"• TTPV: {metrics.get('time_to_peak_velocity', 0):.3f}"
        
        for channel_id, config in self.server_config.items():
            if config.get('metrics', False):
                try:
                    channel = self.get_channel(channel_id)
                    if channel:
                        await channel.send(message)
                except Exception as e:
                    self.logger.error(f"Ошибка отправки метрик: {e}")
                    
    async def send_session_report(self, report: Dict):
        """Отправить отчет о сессии"""
        embed = discord.Embed(
            title="📋 Отчет о сессии",
            color=discord.Color.green(),
            timestamp=datetime.now()
        )
        
        embed.add_field(name="🎮 Игра", value=report.get('game', 'Неизвестно'), inline=True)
        embed.add_field(name="⏱️ Длительность", value=f"{report.get('duration', 0)} сек", inline=True)
        embed.add_field(name="🎯 Стиль", value=report.get('style', 'Не определен'), inline=True)
        
        if 'metrics' in report:
            metrics = report['metrics']
            embed.add_field(name="📈 Sample Entropy", value=f"{metrics.get('sample_entropy', 0):.3f}", inline=True)
            embed.add_field(name="🎯 MAD", value=f"{metrics.get('maximum_absolute_deviation', 0):.2f}", inline=True)
            embed.add_field(name="⚡ TTPV", value=f"{metrics.get('time_to_peak_velocity', 0):.3f}", inline=True)
            
        for channel_id, config in self.server_config.items():
            if config.get('reports', False):
                try:
                    channel = self.get_channel(channel_id)
                    if channel:
                        await channel.send(embed=embed)
                except Exception as e:
                    self.logger.error(f"Ошибка отправки отчета: {e}")

def create_discord_bot(token: str, mouseai_instance=None) -> DiscordBot:
    """Создать Discord бота"""
    return DiscordBot(token, mouseai_instance)

# Пример использования
if __name__ == "__main__":
    import os
    
    # Получаем токен из переменной окружения
    token = os.getenv('DISCORD_BOT_TOKEN')
    
    if not token:
        print("❌ Установите DISCORD_BOT_TOKEN")
        exit(1)
        
    bot = create_discord_bot(token)
    
    try:
        bot.run(token)
    except KeyboardInterrupt:
        print("� Остановка Discord бота...")