# Financial Times Scraper

## Опис

Простий асинхронний парсер новин з сайту [Financial Times](https://www.ft.com/world).  
Збирає новини, зберігає їх у базу даних PostgreSQL.

- Під час першого запуску можна збирати статті за останню годину (з можливістю розширення).  
- Надалі запускається щогодини і збирає тільки нові статті.  
- Уникнення дублювання статей.  
- Логування процесу у консоль. 


## Вимоги

- Python 3.9+  
- PostgreSQL  
- Docker (для розгортання)  

## Встановлення

1. Клонувати репозиторій:

```bash
git clone <URL_твоєї_репи>
cd financial-times-scraper
```


2. Створіть і активуйте віртуальне середовище (рекомендовано):
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

3. Встановіть залежності:
```bash
pip install -r requirements.txt
```
4. Налаштуйте підключення до PostgreSQL (див. financial_times_scraper/app/database.py).

5. Запустіть скрапінг:
```bash
python scraper.py
```

## Використання
Скрипт автоматично запускає цикл збору новин щогодини.

Дані зберігаються у таблицю articles бази PostgreSQL.

## Структура даних статті

```bash
{
  "url": "str",                // Унікальний URL статті
  "title": "str",              // Заголовок
  "content": "str",            // Повний текст статті
  "author": "str",             // Автор (якщо є)
  "published_at": "datetime",  // Дата публікації
  "scraped_at": "datetime",    // Дата та час збору
  "subtitle": "str",           // Підзаголовок (опціонально)
  "tags": ["str"],             // Теги (опціонально)
  "image_url": "str",          // URL головного зображення (опціонально)
  "word_count": "int",         // Кількість слів у тексті
  "reading_time": "str",       // Орієнтовний час читання (опціонально)
  "related_articles": ["str"]  // URL пов'язаних статей (опціонально)
}
```

## Обробка помилок
Парсинг кожної статті виконується в try/except, щоб не зупиняти весь скрапінг через помилки.



Старт з main.py
```
python -m financial_times_scraper.app.main
```