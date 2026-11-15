# resume-bot

[English](#english) | [Русский](#русский)

---

## Русский

Telegram-бот для конвертации резюме из hh.ru в стильный темный PDF.

**Что делает:**
Бот принимает файл `.rtf`, скачанный с hh.ru, парсит его (извлекая контакты, опыт, навыки и образование) и генерирует PDF-файл с кастомной версткой (двухколоночная сетка, темная тема).

**Стек:** Python, aiogram 3, ReportLab, striprtf.

**Запуск:**
1. Установите зависимости: `pip install -r requirements.txt`
2. Создайте `.env` и добавьте `TELEGRAM_TOKEN` (и `PROXY_URL`, если нужно).
3. Запустите: `python bot.py`

**Что ломалось и как починил:**
1. RTF-файлы hh.ru содержат артефакты форматирования (символы `|`, таблицы). Написал парсер, который очищает текст и разбивает его по ключевым заголовкам.
2. Проблемы с отступами и переносами строк в ReportLab. Решил через использование `<br/>` и настройку `ParagraphStyle`.
3. Сетевые таймауты Telegram в WSL. Решил добавлением поддержки SOCKS5-прокси через `aiohttp-socks`.

**Ограничения:** Работает только с форматом `.rtf`. Требует локальной нейросети или API не используется (все парсится локально по регуляркам).

**Лицензия:** MIT

---

## English

Telegram bot for converting hh.ru resumes into stylish dark-themed PDFs.

**What it does:**
The bot accepts an `.rtf` file downloaded from hh.ru, parses it (extracting contacts, experience, skills, and education), and generates a custom-layout PDF (two-column grid, dark theme).

**Stack:** Python, aiogram 3, ReportLab, striprtf.

**Usage:**
1. Install dependencies: `pip install -r requirements.txt`
2. Create `.env` and add `TELEGRAM_TOKEN` (and `PROXY_URL` if needed).
3. Run: `python bot.py`

**What broke & how I fixed it:**
1. hh.ru RTF files contain formatting artifacts (`|` symbols, tables). Wrote a parser that cleans the text and splits it by key headings.
2. Layout issues in ReportLab. Fixed by using `<br/>` and tuning `ParagraphStyle`.
3. Telegram network timeouts in WSL. Fixed by adding SOCKS5 proxy support via `aiohttp-socks`.

**Limitations:** Works only with `.rtf` format.

**License:** MIT