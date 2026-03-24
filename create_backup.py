#!/usr/bin/env python3
"""
Создание бэкапа без Git (только ZIP архив)
"""

import os
import zipfile
import shutil
from pathlib import Path
from datetime import datetime

def create_zip_backup():
    """Создать ZIP бэкап проекта"""
    
    project_path = Path(__file__).resolve().parent
    backup_name = f"mouseai-backup-{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
    backup_path = project_path.parent / backup_name
    
    print("🔐 Создание ZIP бэкапа MouseAI...")
    print(f"📁 Исходная папка: {project_path}")
    print(f"📦 Архив: {backup_path}")
    
    # Проверяем что папка существует
    if not project_path.exists():
        print("❌ Папка проекта не найдена")
        return False
    
    try:
        # Создаем ZIP архив
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(project_path):
                for file in files:
                    file_path = Path(root) / file
                    # Добавляем файл в архив с относительным путем
                    arcname = file_path.relative_to(project_path.parent)
                    zipf.write(file_path, arcname)
        
        print(f"✅ Бэкап создан: {backup_path}")
        print(f"📦 Размер архива: {backup_path.stat().st_size / 1024 / 1024:.2f} MB")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка создания бэкапа: {e}")
        return False

def create_github_instructions():
    """Создать инструкции для GitHub"""
    
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

5️⃣ ЗАГРУЗИТЕ ФАЙЛЫ:
   - На странице репозитория нажмите "Add file" → "Upload files"
   - Перетащите ZIP архив из папки вашего проекта
   - Нажмите "Commit changes"

6️⃣ ПРОВЕРЬТЕ:
   - Зайдите на GitHub
   - Убедитесь что репозиторий PRIVATE (значок замка 🔐)
   - Проверьте что все файлы загрузились
   - Сделайте скриншот или запомните ссылку

==================================================
✅ ПОСЛЕ ВЫПОЛНЕНИЯ НАПИШИТЕ МНЕ:
==================================================

✅ Ссылка на приватный репозиторий: [вставьте ссылку]
✅ Подтверждение что бэкап сделан
✅ Готовность к улучшениям

⚠️ НЕ НАЧИНАЙТЕ УЛУЧШЕНИЯ ПОКА НЕ ПОЛУЧИТЕ МОЕ ПОДТВЕРЖДЕНИЕ!

==================================================
🛡️ ДОПОЛНИТЕЛЬНАЯ ЗАЩИТА:
==================================================

1. Сохраните ZIP архив в облако:
   - Google Drive
   - OneDrive
   - Dropbox
   - Или на флешку

2. Назовите архив: mouseai-backup-20240319.zip

==================================================
"""
    
    instructions_path = Path(__file__).resolve().parent / "github_instructions.txt"
    with open(instructions_path, "w", encoding="utf-8") as f:
        f.write(instructions)
    
    print("📝 Инструкции сохранены в github_instructions.txt")

if __name__ == "__main__":
    print("🚀 Создание бэкапа MouseAI...")
    
    # Создаем ZIP бэкап
    if create_zip_backup():
        # Создаем инструкции
        create_github_instructions()
        print("\n🎉 БЭКАП ГОТОВ!")
        print("🔍 Теперь прочитайте github_instructions.txt")
        print("🚀 Следуйте инструкциям для создания GitHub репозитория")
    else:
        print("❌ Ошибка создания бэкапа")
        exit(1)