#!/usr/bin/env python3
"""
Скрипт для создания приватного бэкапа на GitHub
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def run_command(cmd, cwd=None):
    """Выполнить команду и вернуть результат"""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=True, 
            text=True, 
            cwd=cwd
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def create_backup():
    """Создать приватный бэкап на GitHub"""
    
    # Путь к проекту
    project_path = Path(__file__).resolve().parent
    
    print("🔐 Создание приватного бэкапа MouseAI...")
    print(f"📁 Путь проекта: {project_path}")
    
    # Проверяем что папка существует
    if not project_path.exists():
        print("❌ Папка проекта не найдена")
        return False
    
    # Инициализируем Git
    print("🔧 Инициализация Git...")
    success, stdout, stderr = run_command("git init", cwd=project_path)
    if not success:
        print(f"❌ Ошибка инициализации Git: {stderr}")
        return False
    print("✅ Git инициализирован")
    
    # Добавляем все файлы
    print("📁 Добавление файлов в Git...")
    success, stdout, stderr = run_command("git add .", cwd=project_path)
    if not success:
        print(f"❌ Ошибка добавления файлов: {stderr}")
        return False
    print("✅ Файлы добавлены")
    
    # Проверяем статус
    print("📊 Проверка статуса Git...")
    success, stdout, stderr = run_command("git status", cwd=project_path)
    if success:
        print("Git status:")
        print(stdout)
    
    # Делаем коммит
    print("📝 Создание коммита...")
    commit_msg = "Initial backup: MouseAI original version before mega-update"
    success, stdout, stderr = run_command(f'git commit -m "{commit_msg}"', cwd=project_path)
    if not success:
        print(f"❌ Ошибка коммита: {stderr}")
        return False
    print("✅ Коммит создан")
    
    # Проверяем ветки
    print("🌿 Проверка веток...")
    success, stdout, stderr = run_command("git branch -M main", cwd=project_path)
    if success:
        print("✅ Ветка переименована в main")
    else:
        print(f"⚠️  Ошибка переименования ветки: {stderr}")
    
    print("\n" + "="*60)
    print("✅ ПЕРВАЯ ЧАСТЬ ЗАВЕРШЕНА!")
    print("🔧 Git репозиторий создан и проинициализирован")
    print("📁 Все файлы добавлены и закоммичены")
    print("🌿 Ветка main создана")
    print("\nТеперь нужно:")
    print("1. Создать приватный репозиторий на GitHub")
    print("2. Выполнить команды для подключения к удаленному репозиторию")
    print("3. Запушить код")
    print("="*60)
    
    return True

def create_github_repo_instructions():
    """Создать инструкции для создания GitHub репозитория"""
    
    instructions = """
==================================================
🤖 ИНСТРУКЦИЯ ПО СОЗДАНИЮ ПРИВАТНОГО РЕПОЗИТОРИЯ
==================================================

1️⃣ ОТКРОЙТЕ GITHUB:
   - Перейдите на https://github.com
   - Войдите в свой аккаунт

2️⃣ СОЗДАЙТЕ НОВЫЙ РЕПОЗИТОРИЙ:
   - Нажмите зеленую кнопку "New repository"
   - Или перейдите по ссылке: https://github.com/new

3️⃣ ЗАПОЛНИТЕ ПОЛЯ:
   - Repository name: mouseai-backup-20240319
   - Description: "Original MouseAI backup before global improvements"
   - ⚠️ ВАЖНО: выберите "Private" (приватный)
   - ❌ НЕ ставьте галочки:
     - [ ] Add a README file
     - [ ] Add .gitignore
     - [ ] Choose a license

4️⃣ НАЖМИТЕ "Create repository"

5️⃣ ПОДКЛЮЧИТЕ ЛОКАЛЬНЫЙ РЕПОЗИТОРИЙ:
   Выполните эти команды в терминале:

   cd путь\\к\\папке\\проекта

   # Замените YOUR_USERNAME на ваш GitHub username
   git remote add origin https://github.com/YOUR_USERNAME/mouseai-backup-20240319.git
   
   git branch -M main
   git push -u origin main

6️⃣ ПРОВЕРЬТЕ:
   - Зайдите на GitHub
   - Убедитесь что репозиторий PRIVATE (значок замка 🔐)
   - Проверьте что все файлы загрузились
   - Сделайте скриншот или запомните ссылку

==================================================
📋 ПРИМЕР КОМАНД ДЛЯ ТЕРМИНАЛА:
==================================================

cd путь\\к\\папке\\проекта
git remote add origin https://github.com/ваш-юзернейм/mouseai-backup-20240319.git
git branch -M main
git push -u origin main

==================================================
✅ ПОСЛЕ ВЫПОЛНЕНИЯ НАПИШИТЕ МНЕ:
==================================================

✅ Ссылка на приватный репозиторий: [вставьте ссылку]
✅ Подтверждение что бэкап сделан
✅ Готовность к улучшениям

⚠️ НЕ НАЧИНАЙТЕ УЛУЧШЕНИЯ ПОКА НЕ ПОЛУЧИТЕ МОЕ ПОДТВЕРЖДЕНИЕ!

==================================================
🛡️ ДОПОЛНИТЕЛЬНАЯ ЗАЩИТА (ОПЦИОНАЛЬНО):
==================================================

Создайте ZIP архив всей папки:
- Выделите папку вашего проекта
- ПКМ → "Отправить" → "Сжатая ZIP-папка"
- Назовите "mouseai-backup-20240319.zip"
- Сохраните в облако (Google Drive, OneDrive) или на флешку

==================================================
"""
    
    instructions_path = Path(__file__).resolve().parent / "github_instructions.txt"
    with open(instructions_path, "w", encoding="utf-8") as f:
        f.write(instructions)
    
    print("📝 Инструкции сохранены в github_instructions.txt")
    print("📄 Прочитайте инструкции перед продолжением")

if __name__ == "__main__":
    # Создаем бэкап
    if create_backup():
        # Создаем инструкции
        create_github_repo_instructions()
        print("\n🎉 ПЕРВАЯ ЧАСТЬ ГОТОВА!")
        print("🔍 Теперь прочитайте github_instructions.txt")
        print("🚀 Следуйте инструкциям для создания GitHub репозитория")
    else:
        print("❌ Ошибка создания бэкапа")
        sys.exit(1)