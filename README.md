# Aim/Mouse Behavior Analysis v0.1

A lightweight local Windows desktop tool for passive aim and mouse-behavior analysis.

---

## What it does

- Lets you select a game or genre
- Records a local mouse-activity session (passive — no game memory reading, no injection)
- Saves a JSON session record locally
- Shows a simple summary with metrics and recommendations
- Displays a history of recent sessions

## What it does NOT do

- Does not read game memory
- Does not inject into game processes
- Does not emulate mouse or keyboard input
- Does not bypass anti-cheat
- Does not interfere with gameplay

---

## Requirements

- Windows
- Python 3.12 (или любая совместимая версия)
- PySide6
- pynput

---

## Install dependencies

```powershell
cd путь\к\папке\myapp
python -m pip install -r requirements.txt
```

---

## Run the app

```powershell
cd путь\к\папке\myapp
python app.py
```

---

## How to use

1. Launch the app
2. Select a game or genre from the dropdown
3. Press **▶ Start Session** and move your mouse normally
4. Press **■ Stop Session** when done
5. The app analyzes the session locally and saves a JSON file to `sessions/`
6. The summary appears in the Overview panel
7. Previous sessions are listed in the History panel

---

## Session data

Each session is saved as a JSON file in the `sessions/` folder.

Fields saved per session:
- `version`, `session_id`, `selected_game`, `status`
- `start_time`, `end_time`, `duration_seconds`
- `click_count`, `movement_activity`
- `average_movement_magnitude`, `movement_variability`
- `intensity_score`, `stability_score`
- `activity_label`, `stability_label`, `movement_style`
- `recommendations`

---

## Settings

`settings.json` controls default behavior:

```json
{
  "version": "0.1",
  "default_game": "Universal",
  "sessions_folder": "sessions",
  "show_help_text": true
}
```

---

## Project structure

```
myapp/
  app.py            ← main application (single file, PySide6)
  requirements.txt  ← dependencies
  settings.json     ← user settings
  README.md         ← this file
  sessions/         ← saved session JSON files
```

---

## Version 0.1 limitations

- Simple local metrics only (no advanced ML)
- No polished charts yet
- No advanced settings UI yet
- No session comparison view yet

This is intentional — the goal of v0.1 is a stable, clean, launchable foundation.

---

## AI Integration (added)

### Environment variables

Create `.env` from `.env.example` and set your keys:

```text
OPENAI_API_KEY=your_openai_api_key
SERPAPI_API_KEY=your_serpapi_api_key
COHERE_API_KEY=your_cohere_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
```

### Install

```powershell
pip install -r requirements.txt
```

### Run

```powershell
python app.py
```

### Как работает

- `mouseai/core/ai_sync.py` содержит класс `AISync`, который обращается:
  - `SerpAPI` к `about-carousel` по запросу
  - `OpenAI` к `gpt-4o-mini` для генерации рекомендаций
- `app.py` добавляет кнопку **AI Boost** и выводит ответ в интерфейсе (и в консоли)

### Специфика работы

- Данные SerpAPI обрабатываются в `mouseai/integration/serpapi_client.py`
- Запросы OpenAI выполняются в `mouseai/integration/openai_client.py`
- Можно расширить Cohere/Anthropic по той же схеме

## Roadmap

- **Phase 1** — Stable base ✔
- **Phase 2** — Improved UI layout
- **Phase 3** — History panel improvements
- **Phase 4** — Settings panel UI
- **Phase 5** — Better analysis and summaries
- **Phase 6** — Optional local charts
